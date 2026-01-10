from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at","actor","action","entity_type","entity_id","result")
    list_filter = ("action","result","entity_type")
    search_fields = ("entity_id","actor__username","reason_code")
