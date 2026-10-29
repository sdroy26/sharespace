from datetime import timedelta
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from accounts.models import User
from audit.services import record_event
from notifications.services import notify
from resources.models import Resource,EligibilityRequirement,UserEligibility
from .models import Booking,ConditionReport,IncidentReport
ACTIVE=(Booking.Status.PENDING,Booking.Status.APPROVED,Booking.Status.CHECKED_OUT,Booking.Status.OVERDUE)
def overlap_q(start,end):return Q(start__lt=end,end__gt=start)
def validate_request(user,resource,start,end,exclude_booking=None):
 errors=[];now=timezone.now()
 if resource.publication_status!=Resource.Publication.PUBLISHED:errors.append('This resource is not published for borrowing.')
 if resource.status!=Resource.Status.AVAILABLE:errors.append('This resource is unavailable or under maintenance.')
 if start<=now+timedelta(hours=resource.advance_notice_hours):errors.append(f'Requests require at least {resource.advance_notice_hours} hour(s) advance notice.')
 if end<=start:errors.append('End time must be after start time.')
 if end-start>timedelta(hours=resource.max_duration_hours):errors.append(f'Maximum booking duration is {resource.max_duration_hours} hour(s).')
 if user.institution!=resource.institution:errors.append('This resource is restricted to its institution.')
 if resource.training_required and not user.training_verified:errors.append('Required training is not yet verified on your profile.')
 if resource.owner.verification_status!=User.Verification.VERIFIED and not resource.owner.is_superuser:errors.append('The resource owner is not yet verified.')
 active_count=Booking.objects.filter(borrower=user,status__in=ACTIVE).exclude(pk=exclude_booking).count()
 if active_count>=resource.max_active_bookings:errors.append(f'Your active booking limit ({resource.max_active_bookings}) has been reached.')
 conflicts=Booking.objects.filter(resource=resource,status__in=(Booking.Status.APPROVED,Booking.Status.CHECKED_OUT,Booking.Status.OVERDUE)).filter(overlap_q(start,end))
 if exclude_booking:conflicts=conflicts.exclude(pk=exclude_booking)
 if conflicts.exists():errors.append('That time overlaps an existing reservation.')
 windows=resource.availability_windows.filter(start__lte=start,end__gte=end)
 if resource.availability_windows.exists() and not windows.exists():errors.append('The selected time is outside the resource availability windows.')
 return errors
def create_request(user,resource,start,end,purpose):
 with transaction.atomic():
  resource=Resource.objects.select_for_update().get(pk=resource.pk)
  errors=validate_request(user,resource,start,end)
  conflict_message='That time overlaps an existing reservation.'
  non_conflict_errors=[e for e in errors if e != conflict_message]
  if non_conflict_errors:raise ValueError(' '.join(non_conflict_errors))
  duplicate=Booking.objects.filter(resource=resource,borrower=user,status__in=(Booking.Status.PENDING,Booking.Status.WAITLISTED,Booking.Status.APPROVED)).filter(overlap_q(start,end)).exists()
  if duplicate:raise ValueError('You already have a request for an overlapping time.')
  conflict=Booking.objects.filter(resource=resource,status__in=(Booking.Status.APPROVED,Booking.Status.CHECKED_OUT,Booking.Status.OVERDUE)).filter(overlap_q(start,end)).exists()
  status=Booking.Status.WAITLISTED if conflict else Booking.Status.PENDING
  booking=Booking.objects.create(resource=resource,borrower=user,start=start,end=end,purpose=purpose,status=status)
  record_event(user,'BOOKING_WAITLISTED' if status==Booking.Status.WAITLISTED else 'BOOKING_REQUESTED',booking,'Placed on waitlist' if status==Booking.Status.WAITLISTED else 'Booking request submitted')
  notify(user,'BOOKING_STATUS','Booking request received' if status==Booking.Status.PENDING else 'Added to waiting list',f'{resource.name}: {booking.get_status_display()}.','/bookings/%s/'%booking.pk)
  if status==Booking.Status.PENDING:notify(resource.owner,'BOOKING_REQUEST','New booking request',f'{user.username} requested {resource.name}.','/owner/requests/%s/'%booking.pk)
  return booking
def decide_booking(actor,booking,decision,reason=''):
 with transaction.atomic():
  booking=Booking.objects.select_for_update().select_related('resource','borrower').get(pk=booking.pk)
  if booking.resource.owner_id!=actor.id and actor.role!='MANAGER' and not actor.is_superuser:raise PermissionError('You cannot decide this booking.')
  if booking.status!=Booking.Status.PENDING:raise ValueError('Only pending requests can be decided.')
  if decision=='approve':
   errors=validate_request(booking.borrower,booking.resource,booking.start,booking.end,exclude_booking=booking.pk)
   if errors:raise ValueError('Cannot approve: '+' '.join(errors))
   booking.status=Booking.Status.APPROVED;summary='Booking approved'
  else:
   if not reason.strip():raise ValueError('A rejection reason is required.')
   booking.status=Booking.Status.REJECTED;summary='Booking rejected'
  booking.decision_reason=reason.strip();booking.decided_at=timezone.now();booking.save()
  record_event(actor,'BOOKING_'+booking.status,booking,summary,{'reason':booking.decision_reason})
  notify(booking.borrower,'BOOKING_STATUS',summary,f'{booking.resource.name}: {booking.decision_reason or "Your request was approved."}',f'/bookings/{booking.pk}/')
  return booking
def cancel_booking(actor,booking):
 with transaction.atomic():
  booking=Booking.objects.select_for_update().select_related('resource').get(pk=booking.pk)
  if booking.borrower_id!=actor.id and booking.resource.owner_id!=actor.id and actor.role!='MANAGER' and not actor.is_superuser:raise PermissionError
  if booking.status not in (Booking.Status.PENDING,Booking.Status.APPROVED,Booking.Status.WAITLISTED):raise ValueError('This booking can no longer be cancelled.')
  booking.status=Booking.Status.CANCELLED;booking.cancelled_at=timezone.now();booking.save(update_fields=['status','cancelled_at','updated_at'])
  record_event(actor,'BOOKING_CANCELLED',booking,'Booking cancelled');notify(booking.borrower,'BOOKING_CANCELLED','Booking cancelled',booking.resource.name,f'/bookings/{booking.pk}/')
  promote_waitlist(booking.resource,booking.start,booking.end,actor)
def promote_waitlist(resource,start,end,actor=None):
 # FIFO for requests that fit the released slot; safety-sensitive resources still require owner approval.
 candidate=Booking.objects.filter(resource=resource,status=Booking.Status.WAITLISTED,start__lt=end,end__gt=start).order_by('created_at').first()
 if candidate:
  errors=validate_request(candidate.borrower,resource,candidate.start,candidate.end,exclude_booking=candidate.pk)
  if not errors:
   candidate.status=Booking.Status.PENDING;candidate.save(update_fields=['status','updated_at']);record_event(actor,'WAITLIST_PROMOTED',candidate,'Waitlist entry promoted for owner review');notify(candidate.borrower,'WAITLIST_PROMOTED','A slot may be available',f'{resource.name}: your request is now pending owner approval.',f'/bookings/{candidate.pk}/');notify(resource.owner,'BOOKING_REQUEST','Waitlist request promoted',f'Review promoted request for {resource.name}.',f'/owner/requests/{candidate.pk}/')
def check_in(actor,booking,form):
 with transaction.atomic():
  b=Booking.objects.select_for_update().select_related('resource','borrower').get(pk=booking.pk)
  if b.borrower_id!=actor.id:raise PermissionError
  if b.status!=Booking.Status.APPROVED:raise ValueError('Only approved bookings can check in.')
  now=timezone.now()
  if now < b.start-timedelta(minutes=30) or now>b.end:raise ValueError('Check-in is allowed from 30 minutes before the booking until its end time.')
  report=form.save(commit=False);report.booking=b;report.reporter=actor;report.stage=ConditionReport.Stage.CHECKOUT;report.save()
  b.status=Booking.Status.CHECKED_OUT;b.checked_out_at=now;b.save(update_fields=['status','checked_out_at','updated_at'])
  record_event(actor,'CHECK_IN',b,'Borrower checked in and recorded initial condition');notify(b.resource.owner,'CHECK_IN','Resource checked out',f'{b.resource.name} has been checked out.','/bookings/%s/'%b.pk)
  return b
def return_item(actor,booking,form):
 with transaction.atomic():
  b=Booking.objects.select_for_update().select_related('resource','borrower').get(pk=booking.pk)
  if b.borrower_id!=actor.id and b.resource.owner_id!=actor.id and actor.role!='MANAGER' and not actor.is_superuser:raise PermissionError
  if b.status not in (Booking.Status.CHECKED_OUT,Booking.Status.OVERDUE):raise ValueError('This booking has not been checked out.')
  report=form.save(commit=False);report.booking=b;report.reporter=actor;report.stage=ConditionReport.Stage.RETURN;report.save()
  b.returned_at=timezone.now()
  if b.resource.supervision_required and actor.id==b.borrower_id:
   b.status=Booking.Status.CHECKED_OUT;b.save(update_fields=['returned_at','updated_at'])
   record_event(actor,'RETURN_DECLARED',b,'Borrower declared return; owner confirmation required');notify(b.resource.owner,'RETURN_CONFIRM','Return needs confirmation',f'Confirm the return of {b.resource.name}.',f'/bookings/{b.pk}/')
  else:
   b.status=Booking.Status.RETURNED;b.return_confirmed_by=actor;b.save();record_event(actor,'RETURN_CONFIRMED',b,'Return recorded and confirmed');promote_waitlist(b.resource,b.start,b.end,actor)
  return b
def confirm_return(actor,booking):
 with transaction.atomic():
  b=Booking.objects.select_for_update().select_related('resource').get(pk=booking.pk)
  if b.resource.owner_id!=actor.id and actor.role!='MANAGER' and not actor.is_superuser:raise PermissionError
  if b.returned_at is None or b.status not in (Booking.Status.CHECKED_OUT,Booking.Status.OVERDUE):raise ValueError('No return declaration is awaiting confirmation.')
  b.status=Booking.Status.RETURNED;b.return_confirmed_by=actor;b.save();record_event(actor,'RETURN_CONFIRMED',b,'Owner confirmed return');notify(b.borrower,'RETURN_CONFIRMED','Return confirmed',b.resource.name,f'/bookings/{b.pk}/');promote_waitlist(b.resource,b.start,b.end,actor);return b
