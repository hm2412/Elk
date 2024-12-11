from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from tutorials.models import Meeting, TutorAvailability, TutorProfile
from datetime import datetime
from django.contrib.auth import get_user_model

class DashboardViewTests(TestCase):
    def setUp(self):
     
        self.tutor_user = self.create_tutor_user()
        self.student_user = self.create_student_user() 
        self.admin_user = self.create_admin_user()

    def create_tutor_user(self):
        return get_user_model().objects.create_user(
            username='@janedoe',
            email='jane.doe@example.org',
            password='Password123',
            user_type='Tutor'
        )
    
    def create_student_user(self):
        return get_user_model().objects.create_user(
            username='@charlie',
            email='charlie.johnson@example.org',
            password='Password123',
            user_type='Student'
        )
    
    def create_admin_user(self):
        return get_user_model().objects.create_user(
            username='@johndoe',
            email='john.doe@example.com',
            password='Password123',
            user_type='Admin'
        )
    
    def test_print_availability_slots(self):
       
        TutorAvailability.objects.create(
            tutor=self.tutor_user,
            day='Monday',
            start_time='10:00:00',
            end_time='12:00:00'
        )

        
        self.client.login(username='@janedoe', password='Password123')
        with patch('tutorials.views.get_meetings_sorted', return_value=[]), \
             patch('tutorials.views.tutor_dashboard_context', return_value={}), \
             patch('tutorials.views.TutorProfile.objects.get_or_create', return_value=(TutorProfile(hourly_rate=50, subjects=['Scala']), True)), \
             patch('builtins.print') as mock_print:  
            response = self.client.get(reverse('dashboard'))
        
        mock_print.assert_any_call("Monday: 10:00:00 - 12:00:00")

    def test_print_meeting_details(self):

        Meeting.objects.create(
            tutor=self.tutor_user,
            student=self.student_user,
            date=datetime.now().date(),
            start_time='10:00:00',
            end_time='11:00:00'
        )

        self.client.login(username='@janedoe', password='Password123')
        with patch('tutorials.views.get_meetings_sorted', return_value=[]), \
             patch('tutorials.views.tutor_dashboard_context', return_value={}), \
             patch('tutorials.views.TutorProfile.objects.get_or_create', return_value=(TutorProfile(hourly_rate=50, subjects=['Scala']), True)), \
             patch('builtins.print') as mock_print:  
            response = self.client.get(reverse('dashboard'))

        mock_print.assert_any_call(f"Meeting on {datetime.now().date()}: 10:00:00-11:00:00")

    def test_tutor_dashboard(self):

        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'tutor/dashboard_tutor.html')

    def test_student_dashboard(self):

        self.client.login(username='@charlie', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'student/dashboard_student.html')

    def test_admin_dashboard(self):

        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'admin/dashboard_admin.html')

    def test_invalid_user_type(self):
      
        invalid_user = get_user_model().objects.create_user(
            username='invaliduser',
            email='invalid@example.org',
            password='Password123',
            user_type='invalid'
        )
   
        self.client.login(username='invaliduser', password='Password123')
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'student/dashboard_student.html')