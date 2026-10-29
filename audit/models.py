from django.conf import settings
from django.db import models
class AuditEvent(models.Model):
 actor=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name='audit_events'); action=models.CharField(max_length=50); object_type=models.CharField(max_length=80); object_id=models.CharField(max_length=80); summary=models.CharField(max_length=300); metadata=models.JSONField(default=dict,blank=True); created_at=models.DateTimeField(auto_now_add=True)
 class Meta:ordering=['-created_at']; indexes=[models.Index(fields=['object_type','object_id','created_at'])]
 def __str__(self):return f'{self.action}: {self.summary}'
