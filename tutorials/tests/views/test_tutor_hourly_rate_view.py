from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import TutorProfile
from django.contrib.messages.storage.fallback import FallbackStorage
from tutorials.views import TutorHourlyRateView
from tutorials.forms import TutorHourlyRateForm
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

class TutorHourlyRateFunctionViewTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.tutor_user = get_user_model().objects.get(username='@janedoe')

    def test_tutor_hourly_rate_post_valid(self):
        self.client.login(username='@janedoe', password='Password123')
        data = {
            'hourly_rate': '9.50'
        }
        response = self.client.post(reverse('tutor_hourly_rate'), data)
        tutor_profile = TutorProfile.objects.get(tutor=self.tutor_user)
        self.assertEqual(tutor_profile.hourly_rate, 9.50)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Hourly rate updated successfully')
        self.assertRedirects(response, reverse('dashboard'))

    def test_tutor_hourly_rate_post_no_hourly_rate(self):
        self.client.login(username='@janedoe', password='Password123')
        data = {
            'hourly_rate': ''
        }
        response = self.client.post(reverse('tutor_hourly_rate'), data)
        self.assertFalse(TutorProfile.objects.filter(tutor=self.tutor_user).exists())
        self.assertRedirects(response, reverse('dashboard'))

    def test_tutor_hourly_rate_get_request(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(reverse('tutor_hourly_rate'))
        self.assertRedirects(response, reverse('dashboard'))

class TutorHourlyRateClassViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username='@janedoe', password='Password123')
        self.profile = TutorProfile.objects.create(tutor=self.user, hourly_rate=50)

    def test_get_initial(self):
        request = self.factory.get(reverse('tutor_hourly_rate'))
        request.user = self.user
        view = TutorHourlyRateView()
        view.setup(request)
        initial = view.get_initial()

        profile = TutorProfile.objects.get(tutor=self.user)
        self.assertEqual(initial['hourly_rate'], profile.hourly_rate)
            
    def test_form_valid(self):
        request = self.factory.post(reverse('tutor_hourly_rate'), {'hourly_rate': 100})
        request.user = self.user

        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)
        request._messages = FallbackStorage(request)

        view = TutorHourlyRateView()
        view.setup(request)
        form = TutorHourlyRateForm(data={'hourly_rate': 100})

        self.assertTrue(form.is_valid())
        response = view.form_valid(form)

        profile = TutorProfile.objects.get(tutor=self.user)
        self.assertEqual(profile.hourly_rate, 100)

        messages = list(request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Hourly rate updated successfully.')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))
