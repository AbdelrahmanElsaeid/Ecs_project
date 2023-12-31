from django.contrib import admin
from .models import CertificateAuthority, Certificate
# Register your models here.
admin.site.register(CertificateAuthority)
admin.site.register(Certificate)