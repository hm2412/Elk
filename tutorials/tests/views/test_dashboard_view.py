from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class DashboardViewTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.tutor_user = get_user_model().objects.get(username='@janedoe')
        self.student_user = get_user_model().objects.get(username='@charlie')
        self.admin_user = get_user_model().objects.get(username='@petrapickles')

    def test_tutor_dashboard(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'tutor/dashboard_tutor.html')

    def test_student_dashboard(self):
        self.client.login(username='@charlie', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'student/dashboard_student.html')

    def test_admin_dashboard(self):
        self.client.login(username='@petrapickles', password='Password123')
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
