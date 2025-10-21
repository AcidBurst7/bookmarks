from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Action(models.Model):
    user = models.ForeignKey(
        User,
        related_name='actons',
        on_delete=models.CASCADE
    )
    verb = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['-created']),
        ]
        ordering = ['-created']