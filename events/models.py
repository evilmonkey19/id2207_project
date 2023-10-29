from django.db import models


class Event(models.Model):
    record_number = models.BigIntegerField(blank=True, null=True)
    client_name = models.CharField(max_length=255, blank=False, null=False)
    event_type = models.CharField(max_length=255, blank=False, null=False)
    from_date = models.DateField(blank=False, null=False)
    to_date = models.DateField(blank=False, null=False)
    attendes = models.IntegerField(blank=False, null=False)
    decorations = models.BooleanField(default=False)
    meals = models.BooleanField(default=False)  # Breakfast, lunch, dinner
    drinks = models.BooleanField(default=False)  # soft/hot drinks
    photos_filming = models.BooleanField(default=False)
    parties = models.BooleanField(default=False)
    expected_budget = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)

    _status = models.CharField(max_length=40, choices=[
        ('pending_senior_approval', 'Pending Senior Customer Service Approval'),
        ('pending_finance_approval', 'Pending Finance Manager Approval'),
        ('pending_admin_approval', 'Pending Administration Manager Approval'),
        ('pending_senior_final_approval', 'Pending Senior Customer Service Final Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending_senior_approval')

    def save(self, *args, **kwargs) -> None:
        self.move_to_next_status()
        self.set_record_number()
        super(Event, self).save(*args, **kwargs)

    def set_record_number(self) -> None:
        if self.record_number is not None:
            return
        if Event.objects.count() == 0:
            self.record_number = 1
        else:
            self.record_number = Event.objects.last().record_number + 1

    def move_to_next_status(self) -> None:
        """
        Move the event to the next status
        """
        status_transitions = {
            'pending_senior_approval': 'pending_finance_approval',
            'pending_finance_approval': 'pending_admin_approval',
            'pending_admin_approval': 'pending_senior_final_approval',
            'pending_senior_final_approval': 'approved',
        }
        if self.pk is None \
            or self._status == 'rejected' \
            or self._status == 'approved':
            return
        if self._status in status_transitions:
            self._status = status_transitions[self._status]
        else:
            raise Exception('Invalid status')

