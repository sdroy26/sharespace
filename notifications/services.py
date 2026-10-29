from django.db import transaction
from django.utils import timezone
from .models import Notification
def notify(user,kind,title,message,url=''):
 def create():Notification.objects.create(recipient=user,kind=kind,title=title,message=message,url=url)
 transaction.on_commit(create)
