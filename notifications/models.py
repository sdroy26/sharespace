from django.conf import settings
from django.db import models
class Notification(models.Model):
 recipient=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='notifications'); kind=models.CharField(max_length=40); title=models.CharField(max_length=140); message=models.CharField(max_length=350); url=models.CharField(max_length=240,blank=True); created_at=models.DateTimeField(auto_now_add=True); read_at=models.DateTimeField(null=True,blank=True)
 class Meta:ordering=['-created_at']
 @property
 def is_read(self):return self.read_at is not None
