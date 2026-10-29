from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
class RegisterForm(UserCreationForm):
    email=forms.EmailField(required=True)
    class Meta: model=User; fields=('username','first_name','last_name','email','password1','password2')
    def save(self,commit=True):
        user=super().save(commit=False); user.email=self.cleaned_data['email']; user.role=User.Role.BORROWER; user.verification_status=User.Verification.PENDING
        if commit:user.save()
        return user
class ProfileForm(forms.ModelForm):
    class Meta: model=User; fields=('first_name','last_name','email','institution')
