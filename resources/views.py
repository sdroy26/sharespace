from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404,render,redirect
from django.utils import timezone
from django.utils.text import slugify
from accounts.models import User
from audit.services import record_event
from .models import Resource,ResourceAvailability
from .forms import ResourceForm,AvailabilityForm

def resource_list(request):
 qs=Resource.objects.filter(publication_status=Resource.Publication.PUBLISHED,status=Resource.Status.AVAILABLE).select_related('owner')
 q=request.GET.get('q','').strip(); category=request.GET.get('category',''); location=request.GET.get('location','').strip()
 if q:qs=qs.filter(Q(name__icontains=q)|Q(description__icontains=q)|Q(category__icontains=q))
 if category:qs=qs.filter(category=category)
 if location:qs=qs.filter(location__icontains=location)
 page=Paginator(qs,9).get_page(request.GET.get('page'))
 return render(request,'resources/list.html',{'page_obj':page,'resources':page.object_list,'q':q,'category':category,'location':location,'categories':Resource.Category.choices})
def resource_detail(request,slug):
 resource=get_object_or_404(Resource.objects.select_related('owner'),slug=slug,publication_status=Resource.Publication.PUBLISHED)
 windows=resource.availability_windows.filter(end__gt=timezone.now())[:8]
 return render(request,'resources/detail.html',{'resource':resource,'windows':windows})
@login_required
def owner_resources(request):
 if not request.user.can_manage():return render(request,'errors/403.html',status=403)
 qs=Resource.objects.all() if request.user.role=='MANAGER' or request.user.is_superuser else Resource.objects.filter(owner=request.user)
 return render(request,'owner/resources.html',{'resources':qs})
@login_required
def resource_create(request):
 if request.user.role not in ('OWNER','MANAGER') and not request.user.is_superuser:return render(request,'errors/403.html',status=403)
 form=ResourceForm(request.POST or None,request.FILES or None)
 if request.method=='POST' and form.is_valid():
  resource=form.save(commit=False);resource.owner=request.user;resource.publication_status=Resource.Publication.REVIEW;resource.owner_verified=request.user.verification_status==User.Verification.VERIFIED or request.user.is_superuser;resource.save();record_event(request.user,'RESOURCE_CREATED',resource,f'Created resource {resource.name}');messages.success(request,'Resource saved and sent for institutional review.');return redirect('owner_resources')
 return render(request,'resources/form.html',{'form':form,'heading':'Add a resource'})
@login_required
def resource_edit(request,pk):
 resource=get_object_or_404(Resource,pk=pk)
 if not (request.user.is_superuser or request.user.role=='MANAGER' or resource.owner_id==request.user.id):return render(request,'errors/403.html',status=403)
 form=ResourceForm(request.POST or None,request.FILES or None,instance=resource)
 if request.method=='POST' and form.is_valid():form.save();record_event(request.user,'RESOURCE_UPDATED',resource,'Updated resource details');messages.success(request,'Resource updated.');return redirect('owner_resources')
 return render(request,'resources/form.html',{'form':form,'heading':'Edit resource'})
@login_required
def availability(request,pk):
 resource=get_object_or_404(Resource,pk=pk)
 if not (request.user.is_superuser or request.user.role=='MANAGER' or resource.owner_id==request.user.id):return render(request,'errors/403.html',status=403)
 form=AvailabilityForm(request.POST or None)
 if request.method=='POST' and form.is_valid():obj=form.save(commit=False);obj.resource=resource;obj.save();record_event(request.user,'AVAILABILITY_ADDED',resource,'Added an availability window');messages.success(request,'Availability window added.');return redirect('owner_resources')
 return render(request,'resources/availability.html',{'resource':resource,'form':form,'windows':resource.availability_windows.all()})
