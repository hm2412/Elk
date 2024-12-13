from django.db import models
from django.conf import settings
from datetime import time, timedelta, datetime


class Lesson(models.Model):
    KNOWLEDGE_AREAS = [
        ('c++', 'C++'),
        ('scala', 'Scala'),
        ('java', 'Java'),
        ('python', 'Python'),
        ('ruby', 'Ruby'),
    ]
    TERMS = [
        ('sept-dec', 'September - December'),
        ('jan-april', 'January - April'),
        ('may-july', 'May - July'),
    ]
    VENUE_PREFERENCES = [
        ('online', 'Online'),
        ('onsite', 'Onsite'),
    ]
    DURATIONS    = [
        (30, '30 min'),
        (60, '60 min '),
        (90, '90 min'),
        (120, '120 min'),
    ]

    TIME_CHOICES = [
        (datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time(), f"{hour:02d}:{minute:02d}")
        for hour in range(8, 21) 
        for minute in range(0, 60, 10)
    ]

    DAY_CHOICES=[
            ('mon', 'Monday'),
            ('tue', 'Tuesday'),
            ('wed', 'Wednesday'),
            ('thu', 'Thursday'),
            ('fri', 'Friday'),
            ('sat', 'Saturday'),
            ('sun', 'Sunday'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_request'
    )
    knowledge_area = models.CharField(max_length=50, choices=KNOWLEDGE_AREAS)
    term = models.CharField(max_length=50, choices=TERMS)
    start_time = models.TimeField(null = True, blank = True) 
    duration = models.IntegerField(choices=DURATIONS)  
    end_time = models.TimeField(null=True, editable=False)
    days = models.JSONField()   
    time_of_day = models.CharField(max_length=10, editable=False)
    venue_preference = models.CharField(max_length=100, choices=VENUE_PREFERENCES)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.start_time and self.duration is not None:
            self.time_of_day = self.get_time_of_day()
            start_dt = datetime.combine(datetime.today(), self.start_time)
            self.end_time = (start_dt + timedelta(minutes=self.duration)).time()
        super().save(*args, **kwargs)

    def get_time_of_day(self):
        if time(8, 0) <= self.start_time < time(12, 0):
            return 'morning'
        if time(12, 0) <= self.start_time < time(16, 0):
            return 'afternoon'
        if time(16, 0) <= self.start_time < time(20, 0):
            return 'evening'
        
    def time_range(self):
        if self.start_time and self.end_time:
            return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
        return "No time set"
    
    def formatted_days(self):
        day_mapping = {
            'mon': 'Monday',
            'tue': 'Tuesday',
            'wed': 'Wednesday',
            'thu': 'Thursday',
            'fri': 'Friday',
            'sat': 'Saturday',
            'sun': 'Sunday',
            }
        return ", ".join([day_mapping.get(day, day) for day in self.days])  

    def __str__(self):
        return f"{self.student}'s request for {self.knowledge_area} tutoring"
    