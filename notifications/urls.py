from django.urls import path
from . import views
urlpatterns=[path('notifications/',views.notification_list,name='notifications'),path('notifications/<int:pk>/read/',views.mark_read,name='mark_read'),path('notifications/read-all/',views.mark_all_read,name='mark_all_read')]
