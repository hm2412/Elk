from django.contrib import admin
from .models import TutorProfile, TutorAvailability

# Register your models here.
admin.site.register(TutorProfile)
admin.site.register(TutorAvailability)
