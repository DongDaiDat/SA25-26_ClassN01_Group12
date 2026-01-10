from django.contrib import admin
from .models import GradeRecord, GradeChangeLog, SectionGradePolicy
admin.site.register(GradeRecord)
admin.site.register(GradeChangeLog)
admin.site.register(SectionGradePolicy)
