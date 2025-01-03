from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import time
from django.contrib.messages import get_messages
from tutorials.models import TutorAvailability
from tutorials.views import TutorAvailabilityView
from tutorials.forms import TutorAvailabilityForm

class TutorAvailabilityFunctionViewTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.tutor_user = get_user_model().objects.get(username='@janedoe')

    def test_tutor_availability_create_valid(self):
        data = {
            'monday_enabled': 'on',
            'monday_start_time': '10:00',  
            'monday_end_time': '12:00',
        }

        self.client.login(username='@janedoe', password='Password123')
        response = self.client.post(reverse('tutor_availability'), data)

        monday_availability = TutorAvailability.objects.get(tutor=self.tutor_user, day='Monday')

        self.assertEqual(monday_availability.start_time, time(10, 0))
        self.assertEqual(monday_availability.end_time, time(12, 0))

    def test_tutor_availability_clear_existing(self):
        TutorAvailability.objects.create(
            tutor=self.tutor_user,
            day='Monday',
            start_time=time(8, 0), 
            end_time=time(10, 0),
            is_available=True
        )

        self.client.login(username='@janedoe', password='Password123')

        data = {
            'monday_enabled': 'on',
            'monday_start_time': '10:00',
            'monday_end_time': '12:00',
        }

        self.client.post(reverse('tutor_availability'), data)
        self.assertEqual(TutorAvailability.objects.count(), 1)
        monday_availability = TutorAvailability.objects.get(tutor=self.tutor_user, day='Monday')
        self.assertEqual(monday_availability.start_time, time(10, 0))
        self.assertEqual(monday_availability.end_time, time(12, 0))
    
    def test_tutor_availability_success_message(self):
        self.client.login(username='@janedoe', password='Password123')

        data = {
            'monday_enabled': 'on',
            'monday_start_time': '09:00',
            'monday_end_time': '11:00',
        }

        response = self.client.post(reverse('tutor_availability'), data, follow=True) 

        success_messages = list(response.context['messages'])
        self.assertGreater(len(success_messages), 0)  
        self.assertEqual(str(success_messages[0]), 'Availability updated successfully')

        monday_availability = TutorAvailability.objects.get(tutor=self.tutor_user, day='Monday')
        self.assertEqual(monday_availability.start_time, time(9, 0))
        self.assertEqual(monday_availability.end_time, time(11, 0))

    def test_tutor_availability_access_for_non_logged_in_user_post(self):
        data = {
            'monday_enabled': 'on',
            'monday_start_time': '10:00',
            'monday_end_time': '12:00',
        }
        response = self.client.post(reverse('tutor_availability'), data)
        self.assertRedirects(response, reverse('log_in') + '?next=' + reverse('tutor_availability'))

    def test_tutor_availability_non_post_request(self):
        response = self.client.get(reverse('tutor_availability'))
        self.assertRedirects(response, reverse('log_in') + '?next=' + reverse('tutor_availability'))

    def test_tutor_availability_empty_data(self):
        data = {
            'monday_enabled': 'on',
            'monday_start_time': '',
            'monday_end_time': '',
        }
        response = self.client.post(reverse('tutor_availability'), data)
        self.assertEqual(TutorAvailability.objects.filter(tutor=self.tutor_user, day='Monday').count(), 0)

    def test_tutor_availability_multiple_days(self):
        data = {
            'monday_enabled': 'on',
            'monday_start_time': '10:00',
            'monday_end_time': '12:00',
            'tuesday_enabled': 'on',
            'tuesday_start_time': '14:00',
            'tuesday_end_time': '16:00',
        }
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.post(reverse('tutor_availability'), data)
        
        self.assertEqual(TutorAvailability.objects.filter(tutor=self.tutor_user).count(), 2)

    def test_tutor_availability_post_valid(self):
        self.client.login(username='@janedoe', password='Password123')

        data = {
            'monday_enabled': 'on',
            'monday_start_time': '09:00',
            'monday_end_time': '11:00',
            'tuesday_enabled': 'on',
            'tuesday_start_time': '14:00',
            'tuesday_end_time': '16:00',
        }

        response = self.client.post(reverse('tutor_availability'), data)
        self.assertEqual(TutorAvailability.objects.filter(tutor=self.tutor_user).count(), 2)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertTrue(str(messages[0]).startswith("Availability updated successfully"))

        self.assertRedirects(response, reverse('dashboard'))

    def test_tutor_availability_get_redirect(self):
        response = self.client.get(reverse('tutor_availability'))
        self.assertRedirects(response, reverse('log_in') + '?next=' + reverse('tutor_availability'))

    def test_tutor_availability_get_request(self): 
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(reverse('tutor_availability')) 
        self.assertRedirects(response, reverse('dashboard')) 
         
    def test_tutor_availability_post_request_no_start_time(self): 
        self.client.login(username='@janedoe', password='Password123')
        data = { 'monday_enabled': 'on', 'monday_start_time': '', 'monday_end_time': '12:00', } 
        response = self.client.post(reverse('tutor_availability'), data) 
        self.assertEqual(TutorAvailability.objects.filter(tutor=self.tutor_user).count(), 0) 
         
    def test_tutor_availability_post_request_no_end_time(self): 
        self.client.login(username='@janedoe', password='Password123')
        data = { 'monday_enabled': 'on', 'monday_start_time': '10:00', 'monday_end_time': '', } 
        response = self.client.post(reverse('tutor_availability'), data) 
        self.assertEqual(TutorAvailability.objects.filter(tutor=self.tutor_user).count(), 0) 
         
    def test_tutor_availability_redirect_on_get(self):
        response = self.client.get(reverse('tutor_availability'))
        self.assertRedirects(response, reverse('log_in') + '?next=' + reverse('tutor_availability'))

class TutorAvailabilityViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username='@janedoe', password='Password123')
        self.availability = TutorAvailability.objects.create(tutor=self.user, day='Monday', start_time='09:00', end_time='12:00')

    def test_get_context_data(self):
        request = self.factory.get(reverse('tutor_availability'))
        request.user = self.user
        
        view = TutorAvailabilityView()
        view.setup(request)
        context = view.get_context_data()

        self.assertIn('availability_slots', context)
        self.assertIn('form', context)
        
        self.assertQuerySetEqual(
            context['availability_slots'],
            TutorAvailability.objects.filter(tutor=self.user),
            transform=lambda x: x
        )
        
        self.assertIsInstance(context['form'], TutorAvailabilityForm)


