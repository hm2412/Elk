from django.contrib import admin
# Register your models here.

from .models import TutorAvailability

@admin.register(TutorAvailability)
class TutorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'day', 'start_time', 'end_time', 'is_available')


# Using admin temporarily to test request display