from django.contrib import admin
from .models import Booking,ConditionReport,IncidentReport
class ReadOnlyAuditMixin:pass
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):list_display=('id','resource','borrower','start','end','status');list_filter=('status',);search_fields=('resource__name','borrower__username')
admin.site.register([ConditionReport,IncidentReport])
