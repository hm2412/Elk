
from django.db import models
from django.conf import settings

    

class Review(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    content = models.CharField(max_length=90) 
    review_text = models.TextField()
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # Rating from 1 to 5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.student.username} (Rating: {self.rating})'

    class Meta:
        ordering = ['-created_at']