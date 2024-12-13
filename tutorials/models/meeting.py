
from django.db import models
from tutorials.models.user import User

class Meeting(models.Model):
    """Model for scheduling meetings between tutors and students."""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    DAYS_CHOICES = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]

    TIME_OF_DAY_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
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

    day = models.CharField(
        max_length=30,
        choices=DAYS_CHOICES,  
        default='mon',
        blank=False,
        null=False
    )

    start_time = models.TimeField()
    end_time = models.TimeField()
    time_of_day = models.CharField(
        max_length=20,
        choices=TIME_OF_DAY_CHOICES,  
        default='morning',
        blank=False,
        null=False
    )

    topic = models.CharField(max_length=200)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='scheduled'
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def time_range(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):

        return f"Meeting: {self.tutor.username} with {self.student.username} on {self.date}"