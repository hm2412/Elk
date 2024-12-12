from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Meeting, TutorAvailability, TutorProfile, Lesson
from datetime import datetime, time, timedelta

class ScheduleSessionViewTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        # Get users and set correct types
        self.tutor = get_user_model().objects.get(username='@janedoe')
        self.tutor.user_type = 'Admin'
        self.tutor.save()

        self.student = get_user_model().objects.get(username='@charlie')
        self.student.user_type = 'Student'
        self.student.save()

        # Create tutor profile
        self.tutor_profile = TutorProfile.objects.create(
            tutor=self.tutor,
            hourly_rate=50,
            subjects=['Ruby']
        )

        # Get next Monday
        next_monday = datetime.now()
        while next_monday.weekday() != 0:
            next_monday += timedelta(days=1)
        self.next_monday = next_monday

        # Create tutor availability
        self.availability = TutorAvailability.objects.create(
            tutor=self.tutor,
            day='Monday',
            start_time=time(10, 0),
            end_time=time(12, 0)
        )

        # Create lesson
        self.lesson = Lesson.objects.create(
            student=self.student,
            knowledge_area='Ruby',
            term='sept-dec',
            start_time=time(10, 0),
            duration=60,
            days=['mon'],
            venue_preference='online'
        )

        self.url = reverse('schedule_session', args=[self.student.id])

    def test_schedule_session_valid(self):
        self.client.login(username='@janedoe', password='Password123')
        data = {
            'date': self.next_monday.date().isoformat(),
            'start_time': '10:00',
            'end_time': '11:00',
            'student': self.student.id,
            'meeting_type': 'scheduled'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)

    def test_schedule_session_invalid_time(self):
        self.client.login(username='@janedoe', password='Password123')
        data = {
            'date': self.next_monday.date().isoformat(),
            'start_time': '13:00',
            'end_time': '14:00',
            'student': self.student.id,
            'meeting_type': 'scheduled'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200) 

    def test_schedule_session_unauthorized(self):
        self.client.login(username='@charlie', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
    