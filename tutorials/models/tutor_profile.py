from django.core.validators import  MinValueValidator

from django.db import models

from .user import User

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
    

