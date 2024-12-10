from django.test import TestCase
from django.urls import reverse
from django.http import HttpResponseForbidden
from tutorials.models import User

class UserListViewAccessTests(TestCase):
    
    def setUp(self):
        # Create different types of users
        self.student_user = User.objects.create_user(
            username='student@domain.com',
            email='student@example.com',
            first_name='Student',
            last_name='User',
            user_type='Student',
            password='password'
        )
        
        self.tutor_user = User.objects.create_user(
            username='tutor@domain.com',
            email='tutor@example.com',
            first_name='Tutor',
            last_name='User',
            user_type='Tutor',
            password='password'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin@domain.com',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            user_type='Admin',
            password='password'
        )
    
    def test_student_can_access_students_list_with_permission_message(self):
        self.client.login(username='student@domain.com', password='password')
        response = self.client.get(reverse('user_list', args=['students']))
        self.assertEqual(response.status_code, 403)
    
    def test_tutor_can_access_students_list(self):
        self.client.login(username='tutor@domain.com', password='password')
        response = self.client.get(reverse('user_list', args=['students']))
        self.assertEqual(response.status_code, 200)
    
    def test_admin_can_access_students_list(self):
        self.client.login(username='admin@domain.com', password='password')
        response = self.client.get(reverse('user_list', args=['students']))
        self.assertEqual(response.status_code, 200)
    
    def test_student_can_access_tutors_list_with_permission_message(self):
        self.client.login(username='student@domain.com', password='password')
        response = self.client.get(reverse('user_list', args=['tutors']))
        self.assertEqual(response.status_code, 403)
    
    def test_tutor_can_access_tutors_list(self):
        self.client.login(username='tutor@domain.com', password='password')
        response = self.client.get(reverse('user_list', args=['tutors']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Access Denied")
    
    def test_admin_can_access_tutors_list(self):
        self.client.login(username='admin@domain.com', password='password')
        response = self.client.get(reverse('user_list', args=['tutors']))
        self.assertEqual(response.status_code, 200)
