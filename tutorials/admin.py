from django.contrib import admin
# Register your models here.

from .models import Meeting

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'topic', 'student', 'tutor')  # Customize fields


# Using admin temporarily to test request display