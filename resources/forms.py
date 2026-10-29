from django import forms
from .models import Resource,ResourceAvailability
class ResourceForm(forms.ModelForm):
 class Meta:
  model=Resource; fields=('name','description','category','institution','location','image','status','max_duration_hours','advance_notice_hours','buffer_minutes','eligibility_requirements','training_required','supervision_required','rules','cancellation_policy','max_active_bookings')
  widgets={'description':forms.Textarea(attrs={'rows':4}),'eligibility_requirements':forms.Textarea(attrs={'rows':2}),'rules':forms.Textarea(attrs={'rows':3})}
 def clean_image(self):
  image=self.cleaned_data.get('image')
  if image:
   if image.size>5*1024*1024:raise forms.ValidationError('Image must be 5 MB or smaller.')
   if image.content_type not in ('image/jpeg','image/png','image/webp'):raise forms.ValidationError('Upload a JPG, PNG, or WebP image.')
  return image
class AvailabilityForm(forms.ModelForm):
 class Meta: model=ResourceAvailability; fields=('start','end','note'); widgets={'start':forms.DateTimeInput(attrs={'type':'datetime-local'}),'end':forms.DateTimeInput(attrs={'type':'datetime-local'})}
 def clean(self):
  data=super().clean()
  if data.get('start') and data.get('end') and data['end']<=data['start']:raise forms.ValidationError('End must be after start.')
  return data
