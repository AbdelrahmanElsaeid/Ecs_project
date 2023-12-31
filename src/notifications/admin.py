from django.contrib import admin
from .models import Notification,NotificationAnswer,NotificationType
# Register your models here.
admin.site.register(Notification)
admin.site.register(NotificationAnswer)
admin.site.register(NotificationType)