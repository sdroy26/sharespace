from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    class Role(models.TextChoices): BORROWER='BORROWER','Borrower'; OWNER='OWNER','Resource owner'; MANAGER='MANAGER','Institution manager'
    class Verification(models.TextChoices): PENDING='PENDING','Pending'; VERIFIED='VERIFIED','Verified'; REJECTED='REJECTED','Rejected'
    role=models.CharField(max_length=12,choices=Role.choices,default=Role.BORROWER)
    institution=models.CharField(max_length=120,default='Northstar Campus')
    verification_status=models.CharField(max_length=12,choices=Verification.choices,default=Verification.PENDING)
    training_verified=models.BooleanField(default=False)
    def can_manage(self): return self.is_superuser or self.role in (self.Role.OWNER,self.Role.MANAGER)
