from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from accounts.models import User
from resources.models import Resource
from .models import Booking
from .services import create_request,decide_booking
class BookingServiceTests(TestCase):
 def setUp(self):
  self.owner=User.objects.create_user('owner',password='Pass!12345',role='OWNER',verification_status='VERIFIED')
  self.borrower=User.objects.create_user('borrower',password='Pass!12345',institution='Northstar Campus')
  self.resource=Resource.objects.create(name='Projector',slug='projector',description='HD projector',category='OTHER',owner=self.owner,institution='Northstar Campus',location='AV Store',publication_status='PUBLISHED',owner_verified=True,max_duration_hours=5,advance_notice_hours=0)
  self.start=timezone.now()+timedelta(days=2);self.end=self.start+timedelta(hours=2)
 def test_valid_request_and_approval(self):
  b=create_request(self.borrower,self.resource,self.start,self.end,'Presentation');decide_booking(self.owner,b,'approve','');b.refresh_from_db();self.assertEqual(b.status,Booking.Status.APPROVED)
 def test_overlapping_approved_booking_cannot_be_approved(self):
  first=create_request(self.borrower,self.resource,self.start,self.end,'First');decide_booking(self.owner,first,'approve','')
  second_user=User.objects.create_user('borrower2',password='Pass!12345',institution='Northstar Campus')
  waitlisted=create_request(second_user,self.resource,self.start+timedelta(minutes=20),self.end+timedelta(minutes=20),'Overlap');self.assertEqual(waitlisted.status,Booking.Status.WAITLISTED)
 def test_rejection_requires_reason(self):
  b=create_request(self.borrower,self.resource,self.start,self.end,'Presentation')
  with self.assertRaises(ValueError):decide_booking(self.owner,b,'reject','')
