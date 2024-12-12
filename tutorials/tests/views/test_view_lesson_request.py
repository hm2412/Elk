from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Lesson
from datetime import time

class ViewLessonRequestTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.student = get_user_model().objects.get(username='@charlie')
        self.tutor = get_user_model().objects.get(username='@janedoe')
        self.lesson = Lesson.objects.create(
            student=self.student,
            knowledge_area='Ruby',
            term='sept-dec',
            start_time=time(14, 0),
            days=['mon', 'wed'],
            duration=60,
            venue_preference='online'
        )
        self.url = reverse('view_lesson_request')

    def test_view_lesson_request_student(self):
        self.client.login(username='@charlie', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_lesson_request.html')
        self.assertIn('lesson', response.context)
        self.assertEqual(response.context['lesson'], self.lesson)

    def test_view_lesson_request_no_lesson(self):
        self.lesson.delete()
        self.client.login(username='@charlie', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_lesson_request.html')
        self.assertIn('lesson', response.context)
        self.assertIsNone(response.context['lesson'])

    def test_view_lesson_request_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('log_in') + f'?next={self.url}')
