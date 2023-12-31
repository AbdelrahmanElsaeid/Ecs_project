from django.contrib.auth.backends import ModelBackend

from src.users.utils import hash_email

class EmailAuthBackend(ModelBackend):
    def authenticate(self, email=None, password=None):
        username = hash_email(email)
        return super().authenticate(username=username, password=password)
