from django.test import TestCase
from django.urls import reverse
class PublicPagesTests(TestCase):
 def test_home_and_discovery_render(self):
  self.assertEqual(self.client.get(reverse('home')).status_code,200)
  self.assertEqual(self.client.get(reverse('resource_list')).status_code,200)
