from django.db import models
from django.conf import settings

# Create your models here.

class Task(models.Model):
    project_ref = models.CharField(max_length=50,blank=False, null=False)
    description = models.TextField()
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    priority = models.CharField(
        max_length=1, 
        choices=[("h", "High"),("m", "Medium")],
        default="h"
    )

    