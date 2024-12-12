from django.core.management.base import BaseCommand, CommandError
from tutorials.models import User, Lesson, Meeting, TutorProfile, TutorAvailability

class Command(BaseCommand):
    """Build automation command to unseed the database."""
    
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        """Unseed the database."""

        User.objects.filter(is_staff=False).delete()
        Lesson.objects.all().delete()
        Meeting.objects.all().delete()
        TutorProfile.objects.all().delete()
        TutorAvailability.objects.all().delete()
