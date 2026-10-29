def site_context(request):
 unread=0
 if request.user.is_authenticated:unread=request.user.notifications.filter(read_at__isnull=True).count()
 return {'unread_notifications':unread}
