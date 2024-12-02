from django.core.validators import RegexValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar

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
    
class TutorProfile(models.Model):
    """Model for storing tutor-specific information."""
    
    tutor = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='tutor_profile',
        limit_choices_to={'user_type': 'Tutor'}
    )

    hourly_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )

    subjects = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return f"{self.tutor.username}'s Profile"
    

class TutorAvailability(models.Model):
    """Model for storing tutor availability."""
    
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday')
    ]
    
    tutor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='availability_slots',
        limit_choices_to={'user_type': 'Tutor'}
    )
    
    day = models.CharField(max_length=9, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['tutor', 'day', 'start_time', 'end_time']
        ordering = ['day', 'start_time']
    
    def __str__(self):
        return f"{self.tutor.username}'s availability on {self.day}"
    