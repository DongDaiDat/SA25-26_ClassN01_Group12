from django.contrib import admin
from .models import Enrollment, EnrollmentAttempt, OverrideDecision
admin.site.register(Enrollment)
admin.site.register(EnrollmentAttempt)
admin.site.register(OverrideDecision)
