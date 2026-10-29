from django import forms
from django.utils import timezone
from .models import Booking,ConditionReport,IncidentReport
class BookingForm(forms.ModelForm):
 class Meta: model=Booking;fields=('start','end','purpose');widgets={'start':forms.DateTimeInput(attrs={'type':'datetime-local'}),'end':forms.DateTimeInput(attrs={'type':'datetime-local'}),'purpose':forms.Textarea(attrs={'rows':3,'placeholder':'What will you use this resource for?'})}
 def clean(self):
  data=super().clean();s=data.get('start');e=data.get('end')
  if s and s<=timezone.now():self.add_error('start','Start time must be in the future.')
  if s and e and e<=s:self.add_error('end','End must be after start.')
  return data
class DecisionForm(forms.Form):
 decision=forms.ChoiceField(choices=(('approve','Approve request'),('reject','Reject request')))
 reason=forms.CharField(max_length=350,required=False,widget=forms.Textarea(attrs={'rows':2,'placeholder':'Explain the decision, especially if rejecting.'}))
 def clean(self):
  data=super().clean()
  if data.get('decision')=='reject' and not data.get('reason','').strip():self.add_error('reason','Please explain why this request is being rejected.')
  return data
class ConditionForm(forms.ModelForm):
 class Meta: model=ConditionReport;fields=('condition','notes','damage_visible','image');widgets={'notes':forms.Textarea(attrs={'rows':3})}
 def clean_image(self):
  image=self.cleaned_data.get('image')
  if image and (image.size>5*1024*1024 or image.content_type not in ('image/jpeg','image/png','image/webp')):raise forms.ValidationError('Upload a JPG, PNG, or WebP image under 5 MB.')
  return image
class IncidentForm(forms.ModelForm):
 class Meta: model=IncidentReport;fields=('category','description','severity','image');widgets={'description':forms.Textarea(attrs={'rows':4})}
