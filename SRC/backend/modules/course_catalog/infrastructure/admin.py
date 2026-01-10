from django.contrib import admin
from .models import Course, CoursePrerequisite
admin.site.register(Course)
admin.site.register(CoursePrerequisite)
