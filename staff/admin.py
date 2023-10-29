from typing import Any
from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models.fields.related import ForeignKey
from django.db.models.query import QuerySet
from django.forms.models import ModelChoiceField
from django.http.request import HttpRequest

from staff.models import Recruitment

class RecruitmentAdmin(admin.ModelAdmin):
    list_display = (
        'job_title',
        'requesting_department',
        'contract_type',
        '_status',
    )
    list_filter = (
        'requesting_department',
        'contract_type',
        '_status',
    )
    search_fields = (
        'job_title',
    )
    readonly_fields = (
        'requester',
        '_status',
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        user: User = request.user
        if user.groups.filter(name__in=['HR', 'Human Resources']).exists():
            return Recruitment.objects.filter(_status='pending_hr_approval')
        elif user.groups.filter(name__in=['Production Manager', 'Service Manager']).exists():
            return Recruitment.objects.filter(requester=user)
        return super().get_queryset(request)
    
    def has_change_permission(self, request, obj=None):
        if obj:
            user = request.user
            if user.groups.filter(name__in=['HR', 'Human Resources']).exists() and obj._status != 'pending_hr_approval':
                return False
            elif user.groups.filter(name__in=['Production Manager', 'Service Manager']).exists() and obj._status != 'pending_manager_approval':
                return False
        return super().has_change_permission(request, obj)
    
    def get_readonly_fields(self, request, obj=None):
        user: User = request.user
        if user.groups.filter(name__in=['HR', 'Human Resources']).exists():
            return ['requester', 'requesting_department','years_of_experience','_status']
        elif user.groups.filter(name__in=['Production Manager', 'Service Manager']).exists() \
            and obj._status == 'pending_manager_approval':
            return [f.name for f in self.model._meta.fields]
        elif user.groups.filter(name__in=['Production Manager', 'Service Manager']).exists():
            return [f.name for f in self.model._meta.fields if f.name != 'requester']
        return super().get_readonly_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        user: User = request.user
        if user.is_superuser:
            return []
        return super().get_readonly_fields(request, obj)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.requester = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Recruitment, RecruitmentAdmin)