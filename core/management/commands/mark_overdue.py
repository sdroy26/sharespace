from django.core.management.base import BaseCommand
from django.utils import timezone
from bookings.models import Booking
from audit.services import record_event
from notifications.services import notify
class Command(BaseCommand):
 help='Mark checked-out bookings past their end time as overdue.'
 def handle(self,*args,**opts):
  qs=Booking.objects.filter(status=Booking.Status.CHECKED_OUT,end__lt=timezone.now()).select_related('resource','borrower')
  count=0
  for b in qs:
   b.status=Booking.Status.OVERDUE;b.save(update_fields=['status','updated_at']);record_event(None,'BOOKING_OVERDUE',b,'Booking passed its end time without a recorded return');notify(b.borrower,'OVERDUE','Booking overdue',f'{b.resource.name} is overdue. Please contact the owner and record the return. ',f'/bookings/{b.pk}/');notify(b.resource.owner,'OVERDUE','Resource overdue',f'{b.resource.name} is overdue.',f'/bookings/{b.pk}/');count+=1
  self.stdout.write(self.style.SUCCESS(f'Marked {count} booking(s) overdue.'))
