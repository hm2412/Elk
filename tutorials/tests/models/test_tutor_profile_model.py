from django.test import TestCase
from decimal import Decimal
from tutorials.models import TutorProfile
from django.contrib.auth import get_user_model

class TutorProfileModelTestCase(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']  # Ensure the correct fixture path

    def setUp(self):
        self.user = get_user_model().objects.get(username='@janedoe')
        self.tutor_profile = TutorProfile.objects.create(
            tutor=self.user,
            hourly_rate=Decimal('9.50'),
            subjects=['Java', 'Scala']
        )

    def test_tutor_profile_str_method(self):
        expected_str = f"{self.user.username}'s Profile"
        self.assertEqual(str(self.tutor_profile), expected_str)

    def test_tutor_profile_fields(self):
        self.assertEqual(self.tutor_profile.tutor.username, '@janedoe')
        self.assertEqual(self.tutor_profile.hourly_rate, Decimal('9.50'))
        self.assertEqual(self.tutor_profile.subjects, ['Java', 'Scala'])

    def test_tutor_profile_optional_fields(self):
        tutor_without_profile = get_user_model().objects.create_user(
            username='@joshdoe',
            email='joshdoe@example.org',
            password='Password123',
            user_type='Tutor'
        )
        profile_without_rate = TutorProfile.objects.create(
            
            tutor=tutor_without_profile
        )

        self.assertIsNone(profile_without_rate.hourly_rate)
        self.assertEqual(profile_without_rate.subjects, [])