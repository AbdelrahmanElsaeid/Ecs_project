from django.contrib import admin
from .models import UserProfile, UserSettings,LoginHistory
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(UserSettings)
admin.site.register(LoginHistory)