from django.contrib import admin
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from typing import Any
from financial.models import FinancialRequest

class FinancialRequestAdmin(admin.ModelAdmin):
    list_display = (
        'requesting_department',
        'project_reference',
        'required_amount',
        '_status',
    )
    list_filter = (
        'requesting_department',
        '_status',
    )
    search_fields = (
        'project_reference',
    )
    readonly_fields = (
        '_status',
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        user: User = request.user
        if user.groups.filter(name__startswith='Financial').exists():
            return FinancialRequest.objects.filter(_status='pending_financial_approval')
        return super().get_queryset(request)
    
    def has_change_permission(self, request, obj=None):
        if obj:
            user = request.user
            if user.groups.filter(name__startswith='Financial').exists() \
                and obj._status != 'pending_financial_approval':
                return False
        return super().has_change_permission(request, obj)
    
    def get_readonly_fields(self, request, obj=None):
        user: User = request.user
        if user.is_superuser:
            return []
        if user.groups.filter(name__startswith='Financial').exists():
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)
    
admin.site.register(FinancialRequest, FinancialRequestAdmin)