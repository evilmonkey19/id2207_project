from typing import Any
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from tasks.models import Task

class SubteamGroupFilter(admin.SimpleListFilter):
    title = 'group'
    parameter_name = 'group'

    def lookups(self, request, model_admin):
        groups = Group.objects.filter(name__startswith='Subteam')
        group_tuples = [(group.id, group.name) for group in groups]
        return group_tuples

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(assigned_to__groups__id=self.value())
        return queryset

class TaskAdmin(admin.ModelAdmin): 
    list_display = (
        'project_ref',
        'assigned_to',
        'priority',
        '_status',
    )
    list_filter = (
        SubteamGroupFilter,
        'priority',
    )
    search_fields = (
        'project_ref',
        'assigned_to__username',
    )
    readonly_fields = (
        '_status',
    )

    def get_readonly_fields(self, request, obj=None):
        user: User = request.user
        if user.is_superuser:
            return []
        elif user.groups.filter(name__startswith='Subteam').exists():
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        user: User = request.user
        if user.groups.filter(name__startswith='Subteam').exists():
            return Task.objects.filter(assigned_to=user)
        return super().get_queryset(request)

    def has_change_permission(self, request, obj=None):
        if obj:
            user = request.user
            if user.groups.filter(name__startswith='Subteam').exists() and obj._status != 'pending_subteam_approval':
                return False
            elif user.groups.filter(name=['Service Manager', 'Production Manager']).exists() and obj._status != 'pending_subteam_approval':
                return False
        return super().has_change_permission(request, obj)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'assigned_to':
            kwargs["queryset"] = User.objects.filter(groups__name__startswith='Subteam')
        if db_field.name == 'group':
            kwargs["queryset"] = Group.objects.filter(name__startswith='Subteam')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Task, TaskAdmin)