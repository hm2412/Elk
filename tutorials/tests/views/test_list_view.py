from django.test import TestCase
from django.urls import reverse
from tutorials.models import User

class UserListViewAccessTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.student_user = User.objects.get(username='@charlie')
        self.tutor_user = User.objects.get(username='@janedoe')
        self.admin_user = User.objects.get(username='@petrapickles')

    def test_student_can_access_students_list_with_permission_message(self):
        self.client.login(username='@charlie', password='Password123')
        response = self.client.get(reverse('user_list', args=['students']))
        self.assertEqual(response.status_code, 403)

    def test_tutor_can_access_students_list(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(reverse('user_list', args=['students']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/lists.html")

    def test_admin_can_access_students_list(self):
        self.client.login(username='@petrapickles', password='Password123')
        response = self.client.get(reverse('user_list', args=['students']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/lists.html")

    def test_student_can_access_tutors_list_with_permission_message(self):
        self.client.login(username='@charlie', password='Password123')
        response = self.client.get(reverse('user_list', args=['tutors']))
        self.assertEqual(response.status_code, 403)

    def test_tutor_can_access_tutors_list(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(reverse('user_list', args=['tutors']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/lists.html")
        self.assertContains(response, "Access Denied")

    def test_admin_can_access_tutors_list(self):
        self.client.login(username='@petrapickles', password='Password123')
        response = self.client.get(reverse('user_list', args=['tutors']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/lists.html")
