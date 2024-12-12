from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from tutorials.models import Meeting, TutorAvailability, TutorProfile
from datetime import datetime, time
from django.contrib.auth import get_user_model

class DashboardViewTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.tutor_user = get_user_model().objects.get(username='@janedoe')
        self.student_user = get_user_model().objects.get(username='@charlie')
        self.admin_user = get_user_model().objects.get(username='@petrapickles')

    def test_print_availability_slots(self):
        TutorAvailability.objects.create(
            tutor=self.tutor_user,
            day='Monday',
            start_time=time(10, 0),
            end_time=time(12, 0)
        )

        self.client.login(username='@janedoe', password='Password123')
        with patch('tutorials.views.get_meetings_sorted', return_value=[]), \
             patch('tutorials.views.tutor_dashboard_context', return_value={}), \
             patch('tutorials.views.TutorProfile.objects.get_or_create', return_value=(TutorProfile(hourly_rate=50, subjects=['Scala']), True)), \
             patch('builtins.print') as mock_print:  
            response = self.client.get(reverse('dashboard'))

        mock_print.assert_any_call("Monday: 10:00:00 - 12:00:00")

    def test_print_meeting_details(self):
        Meeting.objects.create(
            tutor=self.tutor_user,
            student=self.student_user,
            date=datetime.now().date(),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )

        self.client.login(username='@janedoe', password='Password123')
        with patch('tutorials.views.get_meetings_sorted', return_value=[]), \
             patch('tutorials.views.tutor_dashboard_context', return_value={}), \
             patch('tutorials.views.TutorProfile.objects.get_or_create', return_value=(TutorProfile(hourly_rate=50, subjects=['Scala']), True)), \
             patch('builtins.print') as mock_print:  
            response = self.client.get(reverse('dashboard'))

        mock_print.assert_any_call(f"Meeting on {datetime.now().date()}: 10:00:00-11:00:00")

    def test_tutor_dashboard(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'tutor/dashboard_tutor.html')

    def test_student_dashboard(self):
        self.client.login(username='@charlie', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'student/dashboard_student.html')

    def test_admin_dashboard(self):
        self.client.login(username='@petrapickles', password='Password123')  # Change back to @petrapickles
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'admin/dashboard_admin.html')

    def test_invalid_user_type(self):
        invalid_user = get_user_model().objects.create_user(
            username='invaliduser',
            email='invalid@example.org',
            password='Password123',
            user_type='invalid'
        )

        self.client.login(username='invaliduser', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'student/dashboard_student.html')

    def test_dashboard_not_logged_in(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('log_in') + '?next=' + reverse('dashboard'))

    def test_student_dashboard_with_no_lesson(self):
        self.client.login(username='@charlie', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/dashboard_student.html')
        self.assertIsNone(response.context.get('lesson'))
