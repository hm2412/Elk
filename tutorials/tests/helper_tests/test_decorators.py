from django.conf import settings
from django.test import TestCase
from django.http import HttpResponse
from django.urls import reverse, path
from tutorials.models import User
from tutorials.helpers import login_prohibited

class LoginProhibitedTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/default_user.json']

    def setUp(self):
        self.home_url = reverse('home')
        self.user = User.objects.get(username='@johndoe')
        self.redirect_url = reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    def test_redirect_logged_in_user(self):
        self.client.login(username=self.user.username, password='Password123')

        response = self.client.get(self.home_url)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)

class UserRoleRequiredTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.student = User.objects.get(username='@charlie')
        self.admin = User.objects.get(username='@petrapickles')
        self.student_id = self.student.id
        self.schedule_session_url = reverse('schedule_session', args=[self.student_id])

    def test_student_access_denied(self):
        self.client.login(username=self.student.username, password='Password123')
        response = self.client.get(self.schedule_session_url)
        self.assertEqual(response.status_code, 403)

    def test_tutor_access_granted(self):
        self.client.login(username=self.admin.username, password='Password123')
        response = self.client.get(self.schedule_session_url)
        self.assertEqual(response.status_code, 200)