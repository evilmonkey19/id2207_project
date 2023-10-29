from django.contrib import admin
from django import forms
from django.contrib.auth.models import User
from events.models import Event

class EventAdminForm(forms.ModelForm):
    approval = forms.ChoiceField(choices=[
        ('approved', 'Approve'),
        ('rejected', 'Reject'),
    ], required=True)

    class Meta:
        model = Event
        fields = '__all__'
        


class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    list_display = ['record_number', 'client_name', '_status']
    search_fields = ['record_number', 'client_name']
    readonly_fields = ['_status',]
    list_filter = ['_status',]

    def get_readonly_fields(self, request, obj=None):
        user: User = request.user
        if user.is_superuser:
            return []
        return self.readonly_fields
    
    def has_change_permission(self, request, obj=None):
        if obj:
            user = request.user
            if user.groups.filter(name='Customer Service').exists() and obj._status != 'created':
                return False
            elif user.groups.filter(name='Senior Customer Service').exists() and obj._status not in ['pending_senior_approval', 'pending_senior_approval_last']:
                return False
            elif user.groups.filter(name='Financial Manager').exists() and obj._status != 'pending_finance_approval':
                return False
            elif user.groups.filter(name='Administration manager').exists() and obj._status != 'pending_admin_approval':
                return False
        return super().has_change_permission(request, obj)
    
    def save_model(self, request, obj, form, change):
        approval = form.cleaned_data['approval']
        if approval == 'rejected':
            obj._status = 'rejected'
        super().save_model(request, obj, form, change)

admin.site.register(Event, EventAdmin)