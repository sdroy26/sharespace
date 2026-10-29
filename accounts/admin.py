from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets=UserAdmin.fieldsets + (('ShareSpace',{'fields':('role','institution','verification_status','training_verified')}),)
    list_display=('username','email','role','institution','verification_status','is_active')
