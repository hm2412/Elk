from django.test import TestCase
from django.urls import reverse
from tutorials.models import User
from tutorials.helpers import (
    handle_students_list,
    handle_tutors_list,
    handle_invalid_or_forbidden_list,
)

class HandleStudentsListTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json', 'tutorials/fixtures/test_meetings.json',]

    def setUp(self):
        self.tutor = User.objects.get(username="@janedoe")
        self.student1 = User.objects.get(username="@charlie")
        self.student2 = User.objects.get(username="@mikemiles")
        self.admin = User.objects.get(username="@petrapickles")

    def test_handle_students_list_as_tutor(self):
        self.client.login(username=self.tutor.username, password='Password123')
        url = reverse('user_list', kwargs={'list_type': 'students'})
        response = self.client.get(url)
        users, title = handle_students_list(response.wsgi_request)

        self.assertEqual(title, "Your Students")
        self.assertIn(self.student1, users)
        self.assertIn(self.student2, users)
        self.assertEqual(response.status_code, 200)

    def test_handle_students_list_as_admin(self):
        self.client.login(username=self.admin.username, password='Password123')
        url = reverse('user_list', kwargs={'list_type': 'students'})
        response = self.client.get(url)
        users, title = handle_students_list(response.wsgi_request)

        self.assertEqual(title, "Student List")
        self.assertIn(self.student1, users)
        self.assertIn(self.student2, users)
        self.assertEqual(response.status_code, 200)

class HandleTutorsListTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json',
                'tutorials/tests/fixtures/tutor_profile.json']
    
    def setUp(self):
        self.tutor1 = User.objects.get(username="@janedoe")
        self.tutor2 = User.objects.get(username="@leslielowe")
        self.student = User.objects.get(username="@charlie")
        self.admin = User.objects.get(username="@petrapickles")
        self.client.force_login(self.student)

    def test_user_list_as_admin_for_tutors(self):
        self.client.login(username=self.admin.username, password='Password123') 
        url = reverse('user_list', kwargs={'list_type': 'tutors'})
        response = self.client.get(url)
        users, title, filters = handle_tutors_list(response.wsgi_request)

        self.assertEqual(title, "Tutor List")
        self.assertIn(self.tutor1, users)
        self.assertIn(self.tutor2, users)
        self.assertEqual(response.status_code, 200)

    def test_handle_tutors_list_without_filters(self):
        self.client.login(username=self.admin.username, password='Password123')
        url = reverse('user_list', kwargs={'list_type': 'tutors'})
        response = self.client.get(url)
        users, title, filters = handle_tutors_list(response.wsgi_request)
        self.assertEqual(title, "Tutor List")
        self.assertIn(self.tutor1, users)
        self.assertIn(self.tutor2, users)

    def test_handle_tutors_list_with_matching_filters(self):
        self.client.login(username=self.admin.username, password='Password123')
        subject_filters = ['python', 'ruby']
        response = self.client.get(reverse('user_list', args=['tutors']), {'subjects': subject_filters})
        self.assertEqual(response.status_code, 200)
        users, title, filters = handle_tutors_list(response.wsgi_request)
        self.assertIn(self.tutor1, users) 
        self.assertIn(self.tutor2, users)

    def test_handle_tutors_list_with_unmatching_filters(self):
        self.client.login(username=self.admin.username, password='Password123')
        subject_filters = ['c++']
        response = self.client.get(reverse('user_list', args=['tutors']), {'subjects': subject_filters})
        self.assertEqual(response.status_code, 200)
        users, title, filters = handle_tutors_list(response.wsgi_request)
        self.assertIn(self.tutor1, users) 
        self.assertNotIn(self.tutor2, users)
    
    class HandleInvalidOrForbiddenListTests(TestCase):
        fixtures = ['tutorials/fixtures/test_users.json']

        def test_invalid_list_type(self):
            result = handle_invalid_or_forbidden_list('courses', 'Tutor')
            self.assertEqual(result, ([], "Invalid List Type", {}))

        def test_invalid_user_type(self):
            result = handle_invalid_or_forbidden_list('students', 'Guest')
            self.assertEqual(result, ([], "Access Denied", {}))

        def test_invalid_list_type_and_user_type(self):
            result = handle_invalid_or_forbidden_list('courses', 'Guest')
            self.assertEqual(result, ([], "Invalid List Type", {}))

        def test_valid_input_for_tutors_list_as_tutor(self):
            result = handle_invalid_or_forbidden_list('tutors', 'Tutor')
            self.assertEqual(result, ([], "Access Denied", {}))

        def test_valid_input_for_students_list_as_admin(self):
            result = handle_invalid_or_forbidden_list('students', 'Admin')
            self.assertEqual(result, ([], "Access Denied", {}))