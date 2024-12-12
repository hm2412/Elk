from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.http import HttpRequest
from tutorials.helpers import admin_dashboard_context, tutor_dashboard_context
from tutorials.models import User

class AdminDashboardContextTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json', 'tutorials/tests/fixtures/lessons.json']

    def test_returns_correct_context(self):
        context = admin_dashboard_context()
        
        self.assertEqual(context['total_students'], 2)
        self.assertEqual(context['total_tutors'], 1)
        self.assertEqual(context['requests'].count(), 2)
        self.assertEqual(context['requests'].first().knowledge_area, 'python')  # Most recent lesson

class TutorDashboardContextTests(TestCase):
    fixtures = ['tutorials/fixtures/test_meetings.json', 
                'tutorials/tests/fixtures/other_users.json',
                'tutorials/tests/fixtures/tutor_profile.json',
                'tutorials/tests/fixtures/tutor_availability.json']
    def setUp(self):
        self.tutor = User.objects.get(username="@janedoe") 
        self.client.login(username=self.tutor.username, password="Password123")
        self.request = HttpRequest()
        self.request.user = self.tutor

    def test_tutor_dashboard_context(self):
        context = tutor_dashboard_context(self.request, self.tutor)
        self.assertEqual(context['tutor_profile'].tutor, self.tutor)
        self.assertTrue('hourly_rate' in context)
        self.assertTrue('subject_choices' in context)
        self.assertEqual(len(context['meetings']), 5)  # 5 meetings in fixture
        meeting = context['meetings'][0]
        self.assertEqual(meeting.tutor, self.tutor)
        self.assertEqual(len(context['availability_slots']), 1)  # 1 availability slot in fixture
        availability = context['availability_slots'][0]
        self.assertEqual(availability.tutor, self.tutor)
        self.assertIn('Monday', [slot.day for slot in context['availability_slots']])
        self.assertIn('calendar_data', context)
        self.assertIsInstance(context['calendar_data'], dict)