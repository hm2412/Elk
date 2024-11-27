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
            'frequency': 3,
            'duration': 60,
            'days': ['mon', 'wed', 'fri'],
            'venue_preference': 'online',
            'student': self.student
        }
 
    def test_form_has_necessary_fields(self):
        form = LessonRequestForm()
        
        self.assertIn('knowledge_area', form.fields)
        self.assertTrue(isinstance(form.fields['knowledge_area'].widget, forms.Select))
        self.assertIn('term', form.fields)
        self.assertIn('frequency', form.fields)
        self.assertIn('duration', form.fields)
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

    def test_invalid_upper_duration(self):
        self.form_input['duration'] = '999'  
        form = LessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('duration', form.errors)
        self.assertEqual(form.errors['duration'], ['Select a valid choice. 999 is not one of the available choices.'])
    
    def test_invalid_lower_duration(self):
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
   