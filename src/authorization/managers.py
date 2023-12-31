from django.db import models
from src.users.utils import get_current_user
from src.authorization.base import get_q_factory

class AuthorizationManager(models.Manager):
    def get_q_factory(self):
        if not hasattr(self, '_q_factory'):
            self._q_factory = get_q_factory(self.model)
        return self._q_factory

    def get_queryset(self):
        qs = self.get_base_queryset()
        user = get_current_user()
        if not user:
            return qs
        q_factory = self.get_q_factory()
        return qs.filter(q_factory(user)).distinct()
    
    def get_base_queryset(self):
        return super().get_queryset()
        
