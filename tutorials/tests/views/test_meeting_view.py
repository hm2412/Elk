
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Meeting
from datetime import datetime, time

class MeetingViewTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.tutor = get_user_model().objects.get(username='@janedoe')
        self.student = get_user_model().objects.get(username='@charlie')
        self.meeting = Meeting.objects.create(
            tutor=self.tutor,
            student=self.student,
            date=datetime.now().date(),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )

    def test_get_meetings_sorted(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('meetings', response.context)
