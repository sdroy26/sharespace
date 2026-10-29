from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views
urlpatterns=[path('admin/',admin.site.urls),path('',include('core.urls')),path('',include('accounts.urls')),path('',include('resources.urls')),path('',include('bookings.urls')),path('',include('operations.urls'))]
if settings.DEBUG: urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler403='core.views.error_403'; handler404='core.views.error_404'; handler500='core.views.error_500'
