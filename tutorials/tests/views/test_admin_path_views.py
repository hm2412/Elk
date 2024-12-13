from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Lesson, Meeting

class AdminPathsViewsTest(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.admin_user = get_user_model().objects.get(username='@petrapickles')
        self.student_user = get_user_model().objects.get(username='@charlie')
        self.client.login(username='@petrapickles', password='Password123')

    def test_create_lesson_request_admin_access(self):
        url = reverse('lesson_request')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_lesson_request_admin_access(self):
        url = reverse('view_lesson_request')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_schedule_session_admin_access(self):
        url = reverse('schedule_session', args=[self.student_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_users_admin_access(self):
        url = reverse('user_list', args=['students'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse('user_list', args=['tutors'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_admin_paths(self):
        self.client.logout()
        urls = [
            reverse('lesson_request'),
            reverse('view_lesson_request'),
            reverse('schedule_session', args=[self.student_user.id]),
            reverse('user_list', args=['students']),
            reverse('user_list', args=['tutors'])
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)

    def test_non_admin_access_denied(self):
        self.client.login(username='@charlie', password='Password123')
        
        # Student-accessible paths return 200
        student_paths = [
            reverse('lesson_request'),
            reverse('view_lesson_request'),
        ]
        for url in student_paths:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        # Admin-only paths return 403
        admin_paths = [
            reverse('schedule_session', args=[self.student_user.id]),
            reverse('user_list', args=['students']),
            reverse('user_list', args=['tutors'])
        ]
        for url in admin_paths:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)
