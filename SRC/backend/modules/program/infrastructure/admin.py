from django.contrib import admin
from .models import Program, CurriculumVersion, CurriculumNode, CurriculumRule

admin.site.register(Program)
admin.site.register(CurriculumVersion)
admin.site.register(CurriculumNode)
admin.site.register(CurriculumRule)
