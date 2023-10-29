from django.db import models

class Recruitment(models.Model):
    contract_type = models.CharField(max_length=5, choices=[("full", "Full-time"),("part", "Part-time")], default="full")
    requester = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    requesting_department = models.CharField(max_length=20, choices=[
        ("admin", "Administration"),
        ("services", "Services"),
        ("production", "Production"),
        ("financial", "Financial"),
    ])
    years_of_experience = models.IntegerField()
    job_title = models.CharField(max_length=255)
    job_description = models.TextField()
    _status = models.CharField(
        max_length=30,
        choices=[
            ('pending_hr_approval', 'Pending HR Approval'),
            ('pending_manager_approval', 'Pending Manager Approval'),
            ('approved', 'Approved'),
        ],
        default='pending_hr_approval'
    )

    def save(self, *args, **kwargs) -> None:
        self.move_to_next_status()
        super(Recruitment, self).save(*args, **kwargs)

    def move_to_next_status(self) -> None:
        """
        Move the event to the next status
        """
        status_transitions = {
            'pending_hr_approval': 'pending_manager_approval',
            'pending_manager_approval': 'approved',
        }
        if self.pk is None \
            or self._status == 'approved':
            return
        if self._status in status_transitions:
            self._status = status_transitions[self._status]
        else:
            raise Exception('Invalid status')
        

