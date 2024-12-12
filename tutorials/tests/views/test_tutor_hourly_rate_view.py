from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import TutorProfile

class TutorHourlyRateTests(TestCase):
    def setUp(self):
        self.tutor_user = self.create_tutor_user()

    def create_tutor_user(self):
        return get_user_model().objects.create_user(
            username='@janedoe',
            email='jane.doe@example.org',
            password='Password123',
            user_type='Tutor'  
        )

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
