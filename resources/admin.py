from django.contrib import admin
from .models import Resource,ResourceAvailability,EligibilityRequirement,UserEligibility
@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):list_display=('name','category','owner','publication_status','status');list_filter=('category','publication_status','status');search_fields=('name','location','owner__username')
admin.site.register([ResourceAvailability,EligibilityRequirement,UserEligibility])
