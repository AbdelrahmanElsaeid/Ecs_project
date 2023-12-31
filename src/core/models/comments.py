from django.db import models
from src.core.models.submissions import Submission
from django.contrib.auth.models import User
from src.documents.models import Document





class Comment(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    text = models.TextField()
    attachment = models.ForeignKey(Document, null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'core'