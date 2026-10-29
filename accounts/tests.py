from django.test import TestCase
from django.urls import reverse
from .models import User
class AccountTests(TestCase):
 def test_registration_cannot_assign_privileged_role(self):
  response=self.client.post(reverse('register'),{'username':'newbie','first_name':'New','last_name':'User','email':'new@example.test','password1':'StrongPass!938','password2':'StrongPass!938','role':'MANAGER'})
  self.assertEqual(response.status_code,302); self.assertEqual(User.objects.get(username='newbie').role,User.Role.BORROWER)
 def test_dashboard_requires_login(self):
  response=self.client.get(reverse('dashboard')); self.assertEqual(response.status_code,302)
