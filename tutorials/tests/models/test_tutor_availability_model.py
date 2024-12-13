from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.models import TutorAvailability
from datetime import time

class TutorAvailabilityTestCase(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.User = get_user_model()
        self.tutor = self.User.objects.get(username='@janedoe')

    def test_create_availability(self):
        availability = TutorAvailability.objects.create(
            tutor=self.tutor,
            day='Monday',
            start_time=time(9, 0),
            end_time=time(12, 0),
            is_available=True
        )
        self.assertEqual(availability.tutor.username, '@janedoe')
        self.assertEqual(availability.day, 'Monday')
        self.assertEqual(availability.start_time, time(9, 0))
        self.assertEqual(availability.end_time, time(12, 0))
        self.assertTrue(availability.is_available)

    def test_unique_availability_constraint(self):
        TutorAvailability.objects.create(
            tutor=self.tutor,
            day='Monday',
            start_time=time(9, 0),
            end_time=time(12, 0),
            is_available=True
        )
        with self.assertRaises(Exception):
            TutorAvailability.objects.create(
                tutor=self.tutor,
                day='Monday',
                start_time=time(9, 0),
                end_time=time(12, 0),
                is_available=True
            )

    def test_availability_is_available_default_true(self):
        availability = TutorAvailability.objects.create(
            tutor=self.tutor,
            day='Tuesday',
            start_time=time(14, 0),
            end_time=time(16, 0)
        )
        self.assertTrue(availability.is_available)

    def test_str_method(self):
        availability = TutorAvailability.objects.create(
            tutor=self.tutor,
            day='Wednesday',
            start_time=time(10, 0),
            end_time=time(14, 0),
            is_available=True
        )
        expected_str = "@janedoe's availability on Wednesday"
        self.assertEqual(str(availability), expected_str)
