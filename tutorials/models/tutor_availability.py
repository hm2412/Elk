
from django.db import models
from .user import User
    

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
