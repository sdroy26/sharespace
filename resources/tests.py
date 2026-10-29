from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from .models import Resource
class ResourceTests(TestCase):
 def setUp(self):
  self.owner=User.objects.create_user('owner',password='Pass!12345',role='OWNER',verification_status='VERIFIED')
  self.r=Resource.objects.create(name='Camera Kit',description='A camera',category='CAMERA',owner=self.owner,location='Media Lab',publication_status='PUBLISHED',owner_verified=True)
 def test_search_page_renders(self):self.assertEqual(self.client.get(reverse('resource_list')+'?q=Camera').status_code,200)
 def test_unrelated_owner_cannot_edit(self):
  other=User.objects.create_user('other',password='Pass!12345',role='OWNER');self.client.force_login(other)
  self.assertEqual(self.client.get(reverse('resource_edit',args=[self.r.pk])).status_code,403)
