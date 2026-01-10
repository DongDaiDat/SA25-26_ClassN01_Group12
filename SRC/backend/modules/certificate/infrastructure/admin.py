from django.contrib import admin
from .models import CertificateDefinition, CertificateIssue
admin.site.register(CertificateDefinition)
admin.site.register(CertificateIssue)
