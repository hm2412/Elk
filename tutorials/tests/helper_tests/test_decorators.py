from django.conf import settings
from django.test import TestCase
from django.urls import reverse
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