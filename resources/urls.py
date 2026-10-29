from django.urls import path
from . import views
urlpatterns=[path('resources/',views.resource_list,name='resource_list'),path('resources/<slug:slug>/',views.resource_detail,name='resource_detail'),path('owner/resources/',views.owner_resources,name='owner_resources'),path('owner/resources/new/',views.resource_create,name='resource_create'),path('owner/resources/<int:pk>/edit/',views.resource_edit,name='resource_edit'),path('owner/resources/<int:pk>/availability/',views.availability,name='availability')]
