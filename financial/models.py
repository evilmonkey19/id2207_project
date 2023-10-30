from django.db import models

class FinancialRequest(models.Model):
    requesting_department = models.CharField(max_length=20, choices=[
        ("admin", "Administration"),
        ("services", "Services"),
        ("production", "Production"),
        ("financial", "Financial"),
    ])
    project_reference = models.CharField(max_length=255)
    required_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()

    _status = models.CharField(
        max_length=30,
        choices=[
            ('pending_financial_approval', 'Pending Financial Approval'),
            ('approved', 'Approved'),
        ],
        default='pending_financial_approval'
    )

    def save(self, *args, **kwargs) -> None:
        self.move_to_next_status()
        super(FinancialRequest, self).save(*args, **kwargs)

    def move_to_next_status(self) -> None:
        """
        Move the event to the next status
        """
        status_transitions = {
            'pending_financial_approval': 'approved',
        }
        if self.pk is None \
            or self._status == 'approved':
            return
        if self._status in status_transitions:
            self._status = status_transitions[self._status]
        else:
            raise Exception('Invalid status')
        
        