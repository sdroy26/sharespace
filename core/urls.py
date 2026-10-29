from django.urls import path
from . import views
urlpatterns=[path('',views.home,name='home'),path('about/',views.about,name='about'),path('privacy/',views.privacy,name='privacy'),path('help/',views.help_page,name='help'),path('dashboard/',views.dashboard,name='dashboard'),path('owner/dashboard/',views.owner_dashboard,name='owner_dashboard')]
