from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count,Q
from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone
from accounts.models import User
from audit.models import AuditEvent
from audit.services import record_event
from bookings.models import Booking,IncidentReport
from resources.models import Resource,EligibilityRequirement
from notifications.services import notify

def manager_required(user):return user.is_authenticated and (user.is_superuser or user.role=='MANAGER')
@login_required
def management_dashboard(request):
 if not manager_required(request.user):return render(request,'errors/403.html',status=403)
 today=timezone.now()
 context={'published_count':Resource.objects.filter(publication_status='PUBLISHED').count(),'pending_resources':Resource.objects.filter(publication_status='REVIEW').count(),'pending_bookings':Booking.objects.filter(status='PENDING').count(),'active_bookings':Booking.objects.filter(status__in=('APPROVED','CHECKED_OUT','OVERDUE')).count(),'overdue':Booking.objects.filter(status='OVERDUE').count(),'open_incidents':IncidentReport.objects.exclude(status__in=('RESOLVED','DISMISSED')).count(),'recent_events':AuditEvent.objects.select_related('actor')[:12],'category_usage':Booking.objects.filter(status='RETURNED',returned_at__gte=today-timedelta(days=30)).values('resource__category').annotate(total=Count('id')).order_by('-total')}
 return render(request,'management/dashboard.html',context)
@login_required
def verification_queue(request):
 if not manager_required(request.user):return render(request,'errors/403.html',status=403)
 resources=Resource.objects.filter(publication_status=Resource.Publication.REVIEW).select_related('owner');users=User.objects.filter(verification_status='PENDING').exclude(role='MANAGER')
 return render(request,'management/verification.html',{'resources':resources,'users':users})
@login_required
@require_POST
def review_resource(request,pk):
 if not manager_required(request.user):return render(request,'errors/403.html',status=403)
 obj=get_object_or_404(Resource,pk=pk);decision=request.POST.get('decision')
 if decision not in ('approve','reject'):messages.error(request,'Invalid review action.')
 else:
  obj.reviewed_by=request.user;obj.owner_verified=obj.owner.verification_status=='VERIFIED' or obj.owner.is_superuser
  obj.publication_status=Resource.Publication.PUBLISHED if decision=='approve' and obj.owner_verified else Resource.Publication.REJECTED if decision=='reject' else Resource.Publication.REVIEW
  obj.save();record_event(request.user,'RESOURCE_'+decision.upper(),obj,f'Resource listing {decision}d');notify(obj.owner,'RESOURCE_REVIEW','Resource listing reviewed',f'{obj.name}: {obj.get_publication_status_display()}.','/owner/resources/')
  messages.success(request,'Resource review saved.')
 return redirect('verification_queue')
@login_required
@require_POST
def review_user(request,pk):
 if not manager_required(request.user):return render(request,'errors/403.html',status=403)
 user=get_object_or_404(User,pk=pk);decision=request.POST.get('decision')
 if decision not in ('approve','reject'):messages.error(request,'Invalid decision.')
 else:
  user.verification_status='VERIFIED' if decision=='approve' else 'REJECTED';user.save(update_fields=['verification_status']);record_event(request.user,'USER_VERIFICATION',user,f'User verification {decision}d');notify(user,'VERIFICATION','Verification updated',f'Your account verification is {user.get_verification_status_display().lower()}.','/profile/');messages.success(request,'Verification decision saved.')
 return redirect('verification_queue')
@login_required
def incidents(request):
 if not manager_required(request.user):return render(request,'errors/403.html',status=403)
 return render(request,'management/incidents.html',{'incidents':IncidentReport.objects.select_related('booking','reporter').all(),'status_choices':IncidentReport.Status.choices})
@login_required
@require_POST
def incident_update(request,pk):
 if not manager_required(request.user):return render(request,'errors/403.html',status=403)
 incident=get_object_or_404(IncidentReport,pk=pk);status=request.POST.get('status');notes=request.POST.get('resolution_notes','').strip()
 if status not in dict(IncidentReport.Status.choices):messages.error(request,'Invalid status.')
 else:
  incident.status=status;incident.assigned_reviewer=request.user;incident.resolution_notes=notes;incident.save();record_event(request.user,'INCIDENT_UPDATED',incident.booking,'Incident status updated',{'status':status});notify(incident.reporter,'INCIDENT_UPDATE','Incident report updated',f'Your incident is now {incident.get_status_display().lower()}.',f'/bookings/{incident.booking_id}/');messages.success(request,'Incident updated.')
 return redirect('management_incidents')
@login_required
def audit_history(request):
 if not manager_required(request.user):return render(request,'errors/403.html',status=403)
 events=AuditEvent.objects.select_related('actor').all();page=Paginator(events,30).get_page(request.GET.get('page'));return render(request,'management/audit.html',{'page_obj':page,'events':page.object_list})
@login_required
def user_management(request):
 if not manager_required(request.user):return render(request,'errors/403.html',status=403)
 return render(request,'management/users.html',{'users':User.objects.order_by('username'),'role_choices':User.Role.choices})
@login_required
@require_POST
def update_user(request,pk):
 if not manager_required(request.user):return render(request,'errors/403.html',status=403)
 user=get_object_or_404(User,pk=pk);role=request.POST.get('role');active=request.POST.get('active')=='yes'
 if user.is_superuser:messages.error(request,'Superuser permissions cannot be changed here.')
 elif role in ('BORROWER','OWNER','MANAGER'):
  user.role=role;user.is_active=active;user.save(update_fields=['role','is_active']);record_event(request.user,'USER_UPDATED',user,'Institution manager updated user access');notify(user,'ACCOUNT','Account access updated','Your ShareSpace account access has been updated.','/profile/');messages.success(request,'User access updated.')
 else:messages.error(request,'Invalid role.')
 return redirect('user_management')
from datetime import timedelta
