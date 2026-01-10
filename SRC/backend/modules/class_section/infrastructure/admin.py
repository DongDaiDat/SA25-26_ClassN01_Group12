from django.contrib import admin
from .models import Room, Section, ScheduleSlot, SectionInstructor
admin.site.register(Room)
admin.site.register(Section)
admin.site.register(ScheduleSlot)
admin.site.register(SectionInstructor)
