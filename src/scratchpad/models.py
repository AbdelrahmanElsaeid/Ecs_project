from django.db import models

# Create your models here.


from django.contrib.auth.models import User

from src.core.models.submissions import Submission


class ScratchPad(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    text = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, null=True, on_delete=models.SET_NULL)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['owner', 'submission'], name='unique_owner_submission'),
        ]

    def is_empty(self):
        return not self.text
