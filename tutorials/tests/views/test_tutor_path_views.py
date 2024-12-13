from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import TutorProfile, TutorAvailability

class TutorPathsViewsTest(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = get_user_model().objects.get(username='@janedoe')
        self.client.login(username='@janedoe', password='Password123')
        
    def test_tutor_hourly_rate_success(self):
        url = reverse('tutor_hourly_rate')
        data = {'hourly_rate': 50.00}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        profile = TutorProfile.objects.get(tutor=self.user)
        self.assertEqual(float(profile.hourly_rate), 50.00)

    def test_tutor_subjects_success(self):
        url = reverse('tutor_subjects')
        data = {'subjects': ['Python', 'Java']}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        profile = TutorProfile.objects.get(tutor=self.user)
        self.assertEqual(profile.subjects, ['Python', 'Java'])

    def test_tutor_availability_success(self):
        url = reverse('tutor_availability')
        data = {
            'monday_enabled': 'on',
            'monday_start_time': '09:00',
            'monday_end_time': '11:00'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        availability = TutorAvailability.objects.filter(tutor=self.user).first()
        self.assertEqual(availability.day, 'Monday')
        self.assertEqual(str(availability.start_time), '09:00:00')

    def test_path_unauthorized_access(self):
        self.client.logout()
        urls = ['tutor_hourly_rate', 'tutor_subjects', 'tutor_availability']
        for url_name in urls:
            response = self.client.post(reverse(url_name), {})
            self.assertEqual(response.status_code, 302)

    def test_path_non_tutor_access(self):
        student = get_user_model().objects.get(username='@charlie')
        self.client.login(username='@charlie', password='Password123')
        urls = ['tutor_hourly_rate', 'tutor_subjects', 'tutor_availability']
        for url_name in urls:
            response = self.client.post(reverse(url_name), {})
            self.assertEqual(response.status_code, 302)
