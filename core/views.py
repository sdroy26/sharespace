from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count,Q
from django.shortcuts import render,redirect
from django.utils import timezone
from accounts.models import User
from resources.models import Resource
from bookings.models import Booking,IncidentReport
from audit.models import AuditEvent

def home(request):
 featured=Resource.objects.filter(publication_status='PUBLISHED',status='AVAILABLE').select_related('owner')[:3]
 return render(request,'core/home.html',{'featured':featured})
def about(request):return render(request,'core/static_page.html',{'title':'About ShareSpace','intro':'Good resources should not sit idle.','paragraphs':['ShareSpace coordinates access to campus equipment and spaces with clear rules, owner approval, eligibility checks, and documented handovers.','It is designed around the full borrowing lifecycle—not just a calendar slot.']})
def privacy(request):return render(request,'core/static_page.html',{'title':'Privacy','intro':'Your campus activity is visible only to the people who need it to operate safely.','paragraphs':['We store account details, booking requests, decisions, condition reports, notifications, and operational audit events to manage borrowing and resolve disputes.','Borrowers see their own bookings. Resource owners see requests and records for resources they manage. Authorised institutional managers can review incidents, verification, and audit history.','Do not upload identity documents or confidential information. Uploaded images should show resource condition only. Data retention and deletion policies must be configured by the deploying institution before production use.']})
def help_page(request):return render(request,'core/static_page.html',{'title':'Help & guidance','intro':'A straightforward borrowing workflow.','paragraphs':['Browse resources and read the Trust & Readiness panel before requesting a slot.','Owners review requests and explain decisions. Approved borrowers record the item condition at check-in and return.','Use Report an issue from a booking if something is late, damaged, missing, unsafe, or incorrectly scheduled.']})
@login_required
def dashboard(request):
 u=request.user
 if u.role=='MANAGER' or u.is_superuser:return redirect('management_dashboard')
 if u.role=='OWNER':return redirect('owner_dashboard')
 qs=Booking.objects.filter(borrower=u).select_related('resource')
 return render(request,'core/dashboard.html',{'upcoming':qs.filter(status='APPROVED',start__gte=timezone.now()).order_by('start')[:5],'pending':qs.filter(status='PENDING').count(),'waitlisted':qs.filter(status='WAITLISTED').count(),'checked_out':qs.filter(status__in=('CHECKED_OUT','OVERDUE')),'recent':qs[:8]})
@login_required
def owner_dashboard(request):
 if not (request.user.role in ('OWNER','MANAGER') or request.user.is_superuser):return render(request,'errors/403.html',status=403)
 resources=Resource.objects.all() if request.user.role=='MANAGER' or request.user.is_superuser else Resource.objects.filter(owner=request.user)
 bookings=Booking.objects.filter(resource__in=resources).select_related('resource','borrower')
 return render(request,'owner/dashboard.html',{'resource_count':resources.count(),'pending':bookings.filter(status='PENDING').count(),'upcoming':bookings.filter(status='APPROVED',start__gte=timezone.now()).order_by('start')[:6],'checked_out':bookings.filter(status__in=('CHECKED_OUT','OVERDUE')),'incidents':IncidentReport.objects.filter(booking__resource__in=resources).exclude(status__in=('RESOLVED','DISMISSED'))[:5],'resources':resources[:5]})
def error_403(request,exception=None):return render(request,'errors/403.html',status=403)
def error_404(request,exception=None):return render(request,'errors/404.html',status=404)
def error_500(request):return render(request,'errors/500.html',status=500)
