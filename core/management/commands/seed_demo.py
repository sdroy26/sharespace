from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from resources.models import Resource,ResourceAvailability
from bookings.models import Booking,ConditionReport,IncidentReport
from audit.services import record_event
from notifications.models import Notification
class Command(BaseCommand):
 help='Create fictional ShareSpace demo accounts and sample data. Safe to run more than once.'
 def handle(self,*args,**opts):
  def user(username,role='BORROWER',**extra):
   obj,created=User.objects.get_or_create(username=username,defaults={'email':f'{username}@example.test','first_name':username.title(),'last_name':'Demo','role':role,'institution':'Northstar Campus','verification_status':'VERIFIED','training_verified':True,**extra})
   if created:obj.set_password('ShareSpaceDemo!26');obj.save()
   return obj
  admin=user('campusadmin','MANAGER',is_staff=True);owner1=user('maya_owner','OWNER');owner2=user('arjun_owner','OWNER');borrowers=[user(n) for n in ('isha_borrower','rohan_borrower','nina_borrower','dev_borrower')]
  for u in (admin,owner1,owner2):
   u.verification_status='VERIFIED';u.save(update_fields=['verification_status'])
  rows=[('DSLR camera kit','CAMERA',owner1,'Media Lab','Training required before solo use.',True,False),('Portable projector','OTHER',owner1,'AV Store','Return with cables and remote.',False,False),('Project laptop','COMPUTING',owner2,'IT Helpdesk','Short-term project use only.',False,False),('Seminar room 2B','ROOM',owner2,'Academic Block B','Leave the room clean and reset furniture.',False,False),('Electronics testing station','LAB',owner1,'Electronics Lab','Authorised users only; do not modify test leads.',True,True),('3D printer access','LAB',owner2,'Fabrication Lab','Supervised operation. Follow material and ventilation rules.',True,True),('Audio recording kit','AUDIO',owner1,'Media Lab','Return microphone, interface, and cables together.',False,False),('Workshop tool kit','TOOLS',owner2,'Workshop','Safety induction required; inspect tools before use.',True,True),('Portable monitor','COMPUTING',owner1,'IT Helpdesk','Use on a stable surface.',False,False),('Project discussion room','ROOM',owner2,'Library Annex','Maximum capacity 6 people.',False,False)]
  resources=[]
  for name,cat,owner,loc,rules,training,supervision in rows:
   r,created=Resource.objects.get_or_create(name=name,defaults={'description':f'{name} available to eligible campus members through a documented handover.','category':cat,'owner':owner,'institution':'Northstar Campus','location':loc,'rules':rules,'training_required':training,'supervision_required':supervision,'max_duration_hours':3 if cat in ('LAB','TOOLS') else 5,'advance_notice_hours':0,'max_active_bookings':2,'publication_status':'PUBLISHED','owner_verified':True,'status':'AVAILABLE'})
   if not created and r.publication_status!='PUBLISHED':r.publication_status='PUBLISHED';r.owner_verified=True;r.save()
   resources.append(r)
  now=timezone.now().replace(second=0,microsecond=0);future=now+timedelta(days=2)
  # Explicit window on a resource demonstrates schedule validation.
  ResourceAvailability.objects.get_or_create(resource=resources[1],start=future.replace(hour=9,minute=0),defaults={'end':future.replace(hour=17,minute=0),'note':'Weekday equipment desk hours'})
  def booking(resource,borrower,start,end,status,purpose):
   b,created=Booking.objects.get_or_create(resource=resource,borrower=borrower,start=start,end=end,defaults={'status':status,'purpose':purpose,'decided_at':now if status not in ('PENDING','WAITLISTED') else None})
   if created:record_event(admin,'DEMO_BOOKING',b,f'Demo booking created with status {status}')
   return b
  b1=booking(resources[1],borrowers[0],future.replace(hour=10),future.replace(hour=11), 'APPROVED','Class presentation')
  b2=booking(resources[6],borrowers[1],future.replace(hour=13),future.replace(hour=14),'PENDING','Record a student podcast')
  b3=booking(resources[2],borrowers[2],now-timedelta(days=3),now-timedelta(days=3)+timedelta(hours=2),'RETURNED','Project demo')
  b4=booking(resources[0],borrowers[3],future.replace(hour=10),future.replace(hour=12),'WAITLISTED','Photography club event')
  b5=booking(resources[3],borrowers[0],now-timedelta(days=1),now-timedelta(days=1)+timedelta(hours=1),'RETURNED','Team meeting')
  for b,stage,condition,notes in [(b3,'CHECKOUT','GOOD','All accessories present at handover.'),(b3,'RETURN','GOOD','Returned clean; charger included.'),(b5,'CHECKOUT','MINOR','Small scuff already visible on desk edge.'),(b5,'RETURN','MINOR','Desk edge scuff remains; no new issue observed.')]:
   ConditionReport.objects.get_or_create(booking=b,stage=stage,defaults={'reporter':b.borrower,'condition':condition,'notes':notes,'damage_visible':condition=='MINOR'})
  IncidentReport.objects.get_or_create(booking=b5,reporter=borrowers[0],category='SCHEDULING',defaults={'description':'The room was occupied for the first ten minutes of the booking. Logged for scheduling review.','severity':'LOW','status':'OPEN'})
  Notification.objects.get_or_create(recipient=borrowers[0],kind='BOOKING_STATUS',title='Demo booking approved',defaults={'message':'Your portable projector request is approved.','url':f'/bookings/{b1.pk}/'})
  Notification.objects.get_or_create(recipient=owner1,kind='BOOKING_REQUEST',title='New demo request',defaults={'message':'Review the audio recording kit request.','url':f'/owner/requests/{b2.pk}/'})
  self.stdout.write(self.style.SUCCESS('Demo data ready. Credentials for all accounts: ShareSpaceDemo!26'))
  self.stdout.write('campusadmin (manager), maya_owner, arjun_owner, isha_borrower, rohan_borrower, nina_borrower, dev_borrower')
