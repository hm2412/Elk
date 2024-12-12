from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Lesson
from django.core.paginator import Paginator
from datetime import time

class ViewLessonRequestTests(TestCase):
    def setUp(self):
        self.student_user = self.create_student_user()
        self.client.login(username='@charlie', password='Password123')
        self.create_lessons()

    def create_student_user(self):
        return get_user_model().objects.create_user(
            username='@charlie',
            email='charlie.johnson@example.org',
            password='Password123',
            user_type='Student'  
        )

    def create_lessons(self):
        lessons = [
            Lesson.objects.create(
                student=self.student_user,
                knowledge_area='python',
                term='sept-dec',
                start_time=time(14, 0), 
                duration=60,
                days=['mon', 'wed'],
                venue_preference='online'
            ) for _ in range(15)  
        ]
        return lessons

    def test_view_lesson_request(self):
        response = self.client.get(reverse('view_lesson_request'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_lesson_request.html')
        self.assertIn('lesson_requests', response.context)

    def test_pagination(self):
        response = self.client.get(reverse('view_lesson_request'))
        self.assertEqual(response.status_code, 200)
       
        lesson_requests = response.context['lesson_requests']
        
        paginator = Paginator(lesson_requests, 10)  
        self.assertEqual(paginator.num_pages, 2)  
        page_obj = paginator.page(1)
        self.assertEqual(len(page_obj.object_list), 10) 

    def test_redirect_for_non_logged_in_user(self):
        self.client.logout()
        response = self.client.get(reverse('view_lesson_request'))
        self.assertRedirects(response, reverse('log_in') + '?next=' + reverse('view_lesson_request'))
