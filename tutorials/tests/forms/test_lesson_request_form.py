from django.test import TestCase
from django.forms import ValidationError
from datetime import time
from tutorials.forms import LessonRequestForm

class LessonRequestFormTestCase(TestCase):
    """Test cases for the LessonRequestForm."""

    def setUp(self):
        self.valid_data = {
            'knowledge_area': 'python',
            'term': 'sept-dec',
            'duration': '60',
            'start_time': '09:00',  
            'days': ['mon', 'tue'],
            'venue_preference': 'online'
        }

        self.invalid_data = {
            'knowledge_area': 'python',
            'term': 'sept-dec',
            'duration': '60',
            'start_time': '07:59',  
            'days': ['mon', 'tue'],
            'venue_preference': 'online'
        }

    def test_valid_start_time(self):
        form = LessonRequestForm(data=self.valid_data)
        self.assertTrue(form.is_valid())  

    def test_invalid_start_time_before_8am(self):
        form = LessonRequestForm(data=self.invalid_data)
        self.assertFalse(form.is_valid())  
        self.assertIn('start_time', form.errors)  

    def test_invalid_start_time_after_8pm(self):

        self.invalid_data['start_time'] = '20:01'
        form = LessonRequestForm(data=self.invalid_data)
        self.assertFalse(form.is_valid())  
        self.assertIn('start_time', form.errors)  