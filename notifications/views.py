from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Notification
@login_required
def notification_list(request):return render(request,'core/notifications.html',{'notifications':request.user.notifications.all()})
@login_required
@require_POST
def mark_read(request,pk):
 n=get_object_or_404(Notification,pk=pk,recipient=request.user);n.read_at=timezone.now();n.save(update_fields=['read_at']);return redirect(n.url or 'notifications')
@login_required
@require_POST
def mark_all_read(request):request.user.notifications.filter(read_at__isnull=True).update(read_at=timezone.now());return redirect('notifications')
