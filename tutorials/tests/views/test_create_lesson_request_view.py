from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.forms import LessonRequestForm
from tutorials.models import Lesson

class CreateLessonRequestViewTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.student_user = get_user_model().objects.get(username='@charlie')

    def test_create_lesson_request_post_valid(self):
        self.client.login(username='@charlie', password='Password123')
        data = {
            'knowledge_area': 'python',
            'term': 'sept-dec',
            'start_time': '14:00',
            'duration': 60,
            'days': ['mon', 'wed'],
            'venue_preference': 'online'
        }
        response = self.client.post(reverse('lesson_request'), data)
        self.assertEqual(Lesson.objects.filter(student=self.student_user).count(), 1)
        self.assertRedirects(response, reverse('dashboard'))

    def test_create_lesson_request_post_invalid(self):
        self.client.login(username='@charlie', password='Password123')
        data = {
            'knowledge_area': '', 
            'term': 'sept-dec',
            'start_time': '14:00',
            'duration': 60,
            'days': ['mon', 'wed'],
            'venue_preference': 'online'
        }
        response = self.client.post(reverse('lesson_request'), data)
        self.assertEqual(Lesson.objects.filter(student=self.student_user).count(), 0)
        self.assertEqual(response.status_code, 200)  

    def test_create_lesson_request_get_request(self):
        self.client.login(username='@charlie', password='Password123')
        response = self.client.get(reverse('lesson_request'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_request.html')
        self.assertIsInstance(response.context['form'], LessonRequestForm)
