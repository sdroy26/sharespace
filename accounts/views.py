from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from .forms import RegisterForm,ProfileForm

def register(request):
    if request.user.is_authenticated:return redirect('dashboard')
    form=RegisterForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        user=form.save(); login(request,user); messages.success(request,'Welcome to ShareSpace. Your account is ready.'); return redirect('dashboard')
    return render(request,'registration/register.html',{'form':form})
@login_required
def profile(request):
    form=ProfileForm(request.POST or None,instance=request.user)
    if request.method=='POST' and form.is_valid():form.save();messages.success(request,'Profile updated.');return redirect('profile')
    return render(request,'core/profile.html',{'form':form})
