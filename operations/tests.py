from django.test import TestCase
from django.urls import reverse
from accounts.models import User
class ManagementPermissionTests(TestCase):
 def test_borrower_cannot_open_management(self):
  u=User.objects.create_user('borrower',password='Pass!12345');self.client.force_login(u)
  self.assertEqual(self.client.get(reverse('management_dashboard')).status_code,403)
