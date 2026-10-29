from django.conf import settings
from django.db import models
from django.utils.text import slugify
class Resource(models.Model):
 class Category(models.TextChoices): CAMERA='CAMERA','Camera & media'; COMPUTING='COMPUTING','Computing'; ROOM='ROOM','Rooms & spaces'; LAB='LAB','Lab equipment'; AUDIO='AUDIO','Audio'; TOOLS='TOOLS','Workshop tools'; OTHER='OTHER','Other'
 class Status(models.TextChoices): AVAILABLE='AVAILABLE','Available'; MAINTENANCE='MAINTENANCE','Maintenance'; SUSPENDED='SUSPENDED','Suspended'
 class Publication(models.TextChoices): DRAFT='DRAFT','Draft'; REVIEW='REVIEW','Awaiting review'; PUBLISHED='PUBLISHED','Published'; REJECTED='REJECTED','Rejected'
 name=models.CharField(max_length=140); slug=models.SlugField(unique=True,blank=True); description=models.TextField(); category=models.CharField(max_length=12,choices=Category.choices)
 owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='owned_resources'); institution=models.CharField(max_length=120,default='Northstar Campus'); location=models.CharField(max_length=160)
 image=models.ImageField(upload_to='resources/%Y/%m/',blank=True); status=models.CharField(max_length=14,choices=Status.choices,default=Status.AVAILABLE); publication_status=models.CharField(max_length=12,choices=Publication.choices,default=Publication.REVIEW)
 max_duration_hours=models.PositiveSmallIntegerField(default=4); advance_notice_hours=models.PositiveSmallIntegerField(default=1); buffer_minutes=models.PositiveSmallIntegerField(default=0); eligibility_requirements=models.TextField(blank=True); training_required=models.BooleanField(default=False); supervision_required=models.BooleanField(default=False); rules=models.TextField(default='Handle with care and return on time.'); cancellation_policy=models.CharField(max_length=240,default='Cancel before the booking starts.'); max_active_bookings=models.PositiveSmallIntegerField(default=2); owner_verified=models.BooleanField(default=False); reviewed_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name='reviewed_resources'); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
 class Meta: ordering=['name']
 def save(self,*args,**kwargs):
  if not self.slug:self.slug=slugify(self.name)[:120]
  if self.owner.role not in ('OWNER','MANAGER') and not self.owner.is_superuser:self.publication_status=self.Publication.DRAFT
  super().save(*args,**kwargs)
 def __str__(self):return self.name
class ResourceAvailability(models.Model):
 resource=models.ForeignKey(Resource,on_delete=models.CASCADE,related_name='availability_windows'); start=models.DateTimeField(); end=models.DateTimeField(); note=models.CharField(max_length=180,blank=True)
 class Meta: ordering=['start']; constraints=[models.CheckConstraint(condition=models.Q(end__gt=models.F('start')),name='availability_end_after_start')]
 def __str__(self):return f'{self.resource}: {self.start} – {self.end}'
class EligibilityRequirement(models.Model):
 resource=models.ForeignKey(Resource,on_delete=models.CASCADE,related_name='requirements'); code=models.SlugField(max_length=50); label=models.CharField(max_length=120); description=models.CharField(max_length=250,blank=True); requires_training=models.BooleanField(default=False); active=models.BooleanField(default=True)
 class Meta: constraints=[models.UniqueConstraint(fields=['resource','code'],name='unique_resource_requirement')]
 def __str__(self):return self.label
class UserEligibility(models.Model):
 class Status(models.TextChoices): PENDING='PENDING','Pending'; APPROVED='APPROVED','Approved'; REJECTED='REJECTED','Rejected'
 user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='eligibility_records'); requirement=models.ForeignKey(EligibilityRequirement,on_delete=models.CASCADE,related_name='user_records'); status=models.CharField(max_length=10,choices=Status.choices,default=Status.PENDING); reviewer=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name='eligibility_reviews'); decision_reason=models.CharField(max_length=250,blank=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
 class Meta: constraints=[models.UniqueConstraint(fields=['user','requirement'],name='unique_user_eligibility')]
