from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import TutorProfile

class TutorSubjectsViewTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.tutor_user = get_user_model().objects.get(username='@janedoe')

    def test_tutor_subjects_post_valid(self):
        self.client.login(username='@janedoe', password='Password123')
        data = {
            'subjects': ['Scala','Ruby']
        }
        response = self.client.post(reverse('tutor_subjects'), data)
        tutor_profile = TutorProfile.objects.get(tutor=self.tutor_user)
        self.assertEqual(tutor_profile.subjects, ['Scala','Ruby'])
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Teaching subjects updated successfully')
        self.assertRedirects(response, reverse('dashboard'))

    def test_tutor_subjects_post_no_subjects(self):
        self.client.login(username='@janedoe', password='Password123')
        data = {
            'subjects': []
        }
        response = self.client.post(reverse('tutor_subjects'), data)
        tutor_profile = TutorProfile.objects.get(tutor=self.tutor_user)
        self.assertEqual(tutor_profile.subjects, [])
        self.assertRedirects(response, reverse('dashboard'))

    def test_tutor_subjects_get_request(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(reverse('tutor_subjects'))
        self.assertRedirects(response, reverse('dashboard'))
