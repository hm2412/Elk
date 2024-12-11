from django.test import TestCase
from django import forms
from tutorials.forms import LessonRequestForm
from tutorials.models import Lesson
from tutorials.models import User

class LessonRequestFormTest(TestCase):

    def setUp(self):
       
        self.student = User.objects.create_user(
            username='@charlie', 
            email='charlie.johnson@example.org', 
            password='Password123', 
            user_type='student'
        )
       
        self.form_input = {
            'knowledge_area': 'python',
            'term': 'sept-dec',
            'time_of_day': 'morning',
            'duration': '60',  
            'start_time': '09:00',  
            'days': ['mon', 'wed', 'fri'],
            'venue_preference': 'online',
        }

    def test_form_has_necessary_fields(self):
        form = LessonRequestForm()

    
        self.assertIn('knowledge_area', form.fields)
        self.assertTrue(isinstance(form.fields['knowledge_area'].widget, forms.Select))
        self.assertIn('term', form.fields)
        self.assertIn('duration', form.fields)
        self.assertIn('start_time', form.fields)
        self.assertTrue(isinstance(form.fields['start_time'].widget, forms.TimeInput))
        self.assertIn('days', form.fields)
        self.assertTrue(isinstance(form.fields['days'].widget, forms.CheckboxSelectMultiple))
        self.assertIn('venue_preference', form.fields)

    def test_valid_form(self):
        form = LessonRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_invalid_knowledge_area(self):
        self.form_input['knowledge_area'] = 'science' 
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('knowledge_area', form.errors)
        self.assertEqual(form.errors['knowledge_area'], ['Select a valid choice. science is not one of the available choices.'])

    def test_invalid_duration(self):
        self.form_input['duration'] = '999'  
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('duration', form.errors)
        self.assertEqual(form.errors['duration'], ['Select a valid choice. 999 is not one of the available choices.'])
        
      
        self.form_input['duration'] = '5' 
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('duration', form.errors)
        self.assertEqual(form.errors['duration'], ['Select a valid choice. 5 is not one of the available choices.'])

    def test_invalid_venue_preference(self):
        self.form_input['venue_preference'] = 'offline'  
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('venue_preference', form.errors)
        self.assertEqual(form.errors['venue_preference'], ['Select a valid choice. offline is not one of the available choices.'])

    def test_empty_days(self):
        self.form_input['days'] = [] 
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('days', form.errors)
        self.assertEqual(form.errors['days'], ['This field is required.'])

    def test_empty_knowledge_area(self):
        self.form_input['knowledge_area'] = ''  
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('knowledge_area', form.errors)
        self.assertEqual(form.errors['knowledge_area'], ['This field is required.'])

    def test_empty_term(self):
        self.form_input['term'] = ''  
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('term', form.errors)
        self.assertEqual(form.errors['term'], ['This field is required.'])

    def test_empty_duration(self):
        self.form_input['duration'] = '' 
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('duration', form.errors)
        self.assertEqual(form.errors['duration'], ['This field is required.'])

    def test_empty_venue_preference(self):
        self.form_input['venue_preference'] = ''  
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('venue_preference', form.errors)
        self.assertEqual(form.errors['venue_preference'], ['This field is required.'])

    def test_invalid_start_time(self):
       
       #wrong formatting of the time
        self.form_input['start_time'] = '9:00 AM'  
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('start_time', form.errors)
        self.assertEqual(form.errors['start_time'], ['Enter a valid time.'])

        # too early - before 8 am
        self.form_input['start_time'] = '07:59'  
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('start_time', form.errors)
        self.assertEqual(form.errors['start_time'], ['The start time must be between 08:00 and 20:00.'])

        # too late - after 8pm
        self.form_input['start_time'] = '20:01'  
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('start_time', form.errors)
        self.assertEqual(form.errors['start_time'], ['The start time must be between 08:00 and 20:00.'])


    def test_valid_start_time(self):
       
        self.form_input['start_time'] = '08:00'  
        form = LessonRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

        self.form_input['start_time'] = '20:00'  
        form = LessonRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

        self.form_input['start_time'] = '10:00' 
        form = LessonRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_valid_multiple_days(self):
        self.form_input['days'] = ['mon', 'wed', 'fri']
        form = LessonRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())


