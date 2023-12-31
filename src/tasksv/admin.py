from django.contrib import admin
from .models import Task,TaskType
# Register your models here.

admin.site.register(Task)

admin.site.register(TaskType)