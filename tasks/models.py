from django.db import models
from django.conf import settings

class Task(models.Model):
    project_ref = models.CharField(max_length=50,blank=False, null=False)
    description = models.TextField()
    group = models.ForeignKey(
        'auth.Group',
        on_delete=models.CASCADE
    )
    assigned_to = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )
    priority = models.CharField(
        max_length=1, 
        choices=[("h", "High"),("m", "Medium")],
        default="m"
    )

    _status = models.CharField(
        max_length=30,
        choices=[
            ('pending_subteam_approval', 'Pending Subteam Approval'),
            ('pending_manager_approval', 'Pending Manager Approval'),
            ('approved', 'Approved'),
        ],
        default='pending_subteam_approval'
    )

    def save(self, *args, **kwargs) -> None:
        self.move_to_next_status()
        super(Task, self).save(*args, **kwargs)

    def move_to_next_status(self) -> None:
        """
        Move the event to the next status
        """
        status_transitions = {
            'pending_subteam_approval': 'pending_manager_approval',
            'pending_manager_approval': 'approved',
        }
        if self.pk is None \
            or self._status == 'approved':
            return
        if self._status in status_transitions:
            self._status = status_transitions[self._status]
        else:
            raise Exception('Invalid status')

    