from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404,render,redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from accounts.models import User
from audit.models import AuditEvent
from audit.services import record_event
from notifications.services import notify
from resources.models import Resource
from .models import Booking,ConditionReport,IncidentReport
from .forms import BookingForm,DecisionForm,ConditionForm,IncidentForm
from .services import create_request,decide_booking,cancel_booking,check_in,return_item,confirm_return

def can_view_booking(user,b):return user.is_superuser or user.role=='MANAGER' or b.borrower_id==user.id or b.resource.owner_id==user.id
@login_required
def booking_list(request):
 qs=Booking.objects.filter(Q(borrower=request.user)|Q(resource__owner=request.user)) if request.user.role!='MANAGER' and not request.user.is_superuser else Booking.objects.all()
 status=request.GET.get('status','')
 if status:qs=qs.filter(status=status)
 page=Paginator(qs.select_related('resource','borrower'),12).get_page(request.GET.get('page'))
 return render(request,'bookings/list.html',{'page_obj':page,'bookings':page.object_list,'statuses':Booking.Status.choices,'status':status})
@login_required
def booking_detail(request,pk):
 booking=get_object_or_404(Booking.objects.select_related('resource','borrower','resource__owner'),pk=pk)
 if not can_view_booking(request.user,booking):return render(request,'errors/403.html',status=403)
 events=AuditEvent.objects.filter(object_type='Booking',object_id=str(booking.pk)).select_related('actor')
 reports=booking.condition_reports.select_related('reporter');incidents=booking.incidents.all()
 return render(request,'bookings/detail.html',{'booking':booking,'events':events,'checkout':reports.filter(stage='CHECKOUT').first(),'return_report':reports.filter(stage='RETURN').first(),'incidents':incidents,'can_manage':request.user.is_superuser or request.user.role=='MANAGER' or booking.resource.owner_id==request.user.id})
@login_required
def request_booking(request,slug):
 resource=get_object_or_404(Resource,slug=slug,publication_status=Resource.Publication.PUBLISHED)
 form=BookingForm(request.POST or None)
 if request.method=='POST' and form.is_valid():
  try:create_request(request.user,resource,form.cleaned_data['start'],form.cleaned_data['end'],form.cleaned_data['purpose']);messages.success(request,'Your request was submitted. Check your booking status for updates.');return redirect('booking_list')
  except ValueError as e:form.add_error(None,str(e))
 return render(request,'bookings/request.html',{'resource':resource,'form':form})
@login_required
def owner_requests(request):
 if not request.user.can_manage():return render(request,'errors/403.html',status=403)
 qs=Booking.objects.select_related('resource','borrower').filter(status__in=(Booking.Status.PENDING,Booking.Status.WAITLISTED))
 if request.user.role=='OWNER' and not request.user.is_superuser:qs=qs.filter(resource__owner=request.user)
 return render(request,'owner/requests.html',{'bookings':qs})
@login_required
def owner_request_detail(request,pk):
 b=get_object_or_404(Booking.objects.select_related('resource','borrower'),pk=pk)
 if not (request.user.is_superuser or request.user.role=='MANAGER' or b.resource.owner_id==request.user.id):return render(request,'errors/403.html',status=403)
 form=DecisionForm(request.POST or None)
 if request.method=='POST' and form.is_valid():
  try:decide_booking(request.user,b,form.cleaned_data['decision'],form.cleaned_data['reason']);messages.success(request,'Decision recorded.');return redirect('owner_requests')
  except (ValueError,PermissionError) as e:form.add_error(None,str(e))
 return render(request,'owner/request_detail.html',{'booking':b,'form':form})
@login_required
@require_POST
def cancel(request,pk):
 b=get_object_or_404(Booking.objects.select_related('resource'),pk=pk)
 try:cancel_booking(request.user,b);messages.success(request,'Booking cancelled.')
 except (ValueError,PermissionError) as e:messages.error(request,str(e))
 return redirect('booking_detail',pk=pk)
@login_required
def checkin_view(request,pk):
 b=get_object_or_404(Booking.objects.select_related('resource'),pk=pk)
 if b.borrower_id!=request.user.id:return render(request,'errors/403.html',status=403)
 form=ConditionForm(request.POST or None,request.FILES or None)
 if request.method=='POST' and form.is_valid():
  try:check_in(request.user,b,form);messages.success(request,'Check-in completed and condition report saved.');return redirect('booking_detail',pk=pk)
  except (ValueError,PermissionError) as e:form.add_error(None,str(e))
 return render(request,'bookings/condition_form.html',{'booking':b,'form':form,'heading':'Check-in condition report','submit_label':'Confirm check-in'})
@login_required
def return_view(request,pk):
 b=get_object_or_404(Booking.objects.select_related('resource'),pk=pk)
 if not can_view_booking(request.user,b):return render(request,'errors/403.html',status=403)
 form=ConditionForm(request.POST or None,request.FILES or None)
 if request.method=='POST' and form.is_valid():
  try:return_item(request.user,b,form);messages.success(request,'Return report saved. If owner confirmation is required, the booking will remain checked out until confirmed.');return redirect('booking_detail',pk=pk)
  except (ValueError,PermissionError) as e:form.add_error(None,str(e))
 return render(request,'bookings/condition_form.html',{'booking':b,'form':form,'heading':'Return condition report','submit_label':'Record return'})
@login_required
@require_POST
def confirm_return_view(request,pk):
 b=get_object_or_404(Booking.objects.select_related('resource'),pk=pk)
 try:confirm_return(request.user,b);messages.success(request,'Return confirmed.')
 except (ValueError,PermissionError) as e:messages.error(request,str(e))
 return redirect('booking_detail',pk=pk)
@login_required
def incident_report(request,pk):
 b=get_object_or_404(Booking,pk=pk)
 if not can_view_booking(request.user,b):return render(request,'errors/403.html',status=403)
 form=IncidentForm(request.POST or None,request.FILES or None)
 if request.method=='POST' and form.is_valid():
  obj=form.save(commit=False);obj.booking=b;obj.reporter=request.user;obj.save();record_event(request.user,'INCIDENT_REPORTED',b,'Incident report submitted',{'category':obj.category});notify(b.resource.owner,'INCIDENT_REPORTED','Incident reported',f'{b.resource.name}: a report needs review.',f'/management/incidents/{obj.pk}/');messages.success(request,'Incident report submitted for review.');return redirect('booking_detail',pk=pk)
 return render(request,'bookings/incident_form.html',{'booking':b,'form':form})
