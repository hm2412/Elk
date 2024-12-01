from django.contrib import admin
from .models import Request

# Register your models here.

# Using admin temporarily to test request display
@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'submitted_at')  # Fields to display in the admin list view
    search_fields = ('title', 'description')  # Fields to enable search
    list_filter = ('submitted_at',)  # Filters to narrow down entries