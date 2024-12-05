from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
import hashlib

class User(AbstractUser):
    """Model used for user authentication, and team member related information."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )

    USER_TYPES = [
        ('Student', 'Student'),
        ('Tutor', 'Tutor'),
        ('Admin', 'Admin')
    ]

    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    user_type = models.CharField(max_length=7, choices=USER_TYPES, default='Student')

    @property
    def gravatar_hash(self):
        email = self.email.strip().lower().encode('utf-8')
        return hashlib.md5(email).hexdigest()

    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        
        return self.gravatar(size=60)
    
from django.conf import settings
from datetime import time, timedelta, datetime

class Lesson(models.Model):

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_request'
    )
    knowledge_area = models.CharField(max_length=50)
    term = models.CharField(max_length=50)
    start_time = models.TimeField(null = True, blank = True) 
    duration = models.IntegerField()  
    end_time = models.TimeField(null=True, editable=False)
    days = models.JSONField()  
    time_of_day = models.CharField(max_length=10, editable=False)
    venue_preference = models.CharField(max_length=100)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

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
        

    def __str__(self):
        return f"{self.student}'s request for {self.knowledge_area} tutoring"
    

class Meeting(models.Model):
    """Model for scheduling meetings between tutors and students."""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    tutor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tutor_meetings',
        limit_choices_to={'user_type': 'Tutor'}
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='student_meetings',
        limit_choices_to={'user_type': 'Student'}
    )

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    topic = models.CharField(max_length=200)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='scheduled'
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"Meeting: {self.tutor.username} with {self.student.username} on {self.date}"
    
