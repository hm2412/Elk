from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model 
from tutorials.models import Meeting

class SaveLessonNotesViewTestCase(TestCase):
    """Tests for the save lesson notes view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.get(username='@charlie')
        self.other_user = get_user_model().objects.get(username='@janedoe')
        self.meeting = Meeting.objects.create(
            student=self.user,
            tutor=self.other_user,
            date='2024-01-01',
            start_time='12:00',
            end_time='13:00'
        )
        self.url = reverse('save_lesson_notes')
        self.form_input = {
            'lesson_id': self.meeting.id,
            'notes': 'Test lesson notes content'
        }

    def test_save_lesson_notes_successful(self):
        self.client.login(username='@charlie', password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.meeting.refresh_from_db()
        self.assertEqual(self.meeting.notes, 'Test lesson notes content')

    def test_save_lesson_notes_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_save_lesson_notes_wrong_user(self):
        self.client.login(username='@charlie', password='Password123')
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 302)
    