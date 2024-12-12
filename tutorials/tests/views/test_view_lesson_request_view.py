from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Lesson
from django.core.paginator import Paginator
from datetime import time

class ViewLessonRequestTests(TestCase):
    def setUp(self):
        self.student_user = self.create_student_user()
        self.client.login(username='studentuser', password='password123')
        self.create_lessons()

    def create_student_user(self):
        return get_user_model().objects.create_user(
            username='studentuser',
            email='student@example.com',
            password='password123',
            user_type='Student'  
        )

    def create_lessons(self):
        lessons = [
            Lesson.objects.create(
                student=self.student_user,
                knowledge_area='python',
                term='sept-dec',
                start_time=time(14, 0),  # Ensure this is a time object
                duration=60,
                days=['mon', 'wed'],
                venue_preference='online'
            ) for _ in range(15)  # Create 15 lesson requests
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
        
        # Extract the queryset from the context
        lesson_requests = response.context['lesson_requests']
        
        # Manually create the paginator with the queryset
        paginator = Paginator(lesson_requests, 10)  # 10 per page
        self.assertEqual(paginator.num_pages, 2)  # 15 items, 10 per page, should result in 2 pages
        page_obj = paginator.page(1)
        self.assertEqual(len(page_obj.object_list), 10)  # First page should have 10 items

    def test_redirect_for_non_logged_in_user(self):
        self.client.logout()
        response = self.client.get(reverse('view_lesson_request'))
        self.assertRedirects(response, reverse('log_in') + '?next=' + reverse('view_lesson_request'))
