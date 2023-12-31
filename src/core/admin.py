from django.contrib import admin
from .models.core import AdvancedSettings
from src.core.models import Submission, EthicsCommission, SubmissionForm, MySubmission, MedicalCategory, Investigator

# Register your models here.
admin.site.register(AdvancedSettings)
admin.site.register(EthicsCommission)
admin.site.register(Submission)
admin.site.register(SubmissionForm)
admin.site.register(MySubmission)
admin.site.register(MedicalCategory)
admin.site.register(Investigator)