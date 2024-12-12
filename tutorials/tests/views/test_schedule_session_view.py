from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from tutorials.models import User, Lesson, Meeting
from tutorials.forms import MeetingForm

class ScheduleSessionViewTests(TestCase):
    """Tests of the session scheduling view."""

    fixtures = ['tutorials/tests/fixtures/other_users.json', 'tutorials/tests/fixtures/lessons.json']
    def setUp(self):
        self.admin = User.objects.get(username='@petrapickles')
        self.tutor = User.objects.get(username='@janedoe')
        self.student = User.objects.get(username='@charlie')
        self.lesson = Lesson.objects.get(student=4)
        self.schedule_session_url = reverse('schedule_session', args=[self.student.id])

    def test_non_admin_access_denied(self):
        self.client.login(username=self.student.username, password='Password123')
        response = self.client.get(self.schedule_session_url)
        self.assertEqual(response.status_code, 403)

    def test_tutor_access_granted(self):
        self.client.login(username=self.admin.username, password='Password123')
        response = self.client.get(self.schedule_session_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/schedule_session.html')
    
    def test_get_schedule_session(self):
        self.client.login(username=self.admin.username, password="Password123")
        response = self.client.get(self.schedule_session_url)
        form = response.context['form']
        self.assertTrue(isinstance(form, MeetingForm))
        self.assertEqual(form.initial['start_time'], self.lesson.start_time)
        self.assertEqual(form.initial['end_time'], self.lesson.end_time)
    
    def test_successful_schedule_meeting(self):
        self.client.login(username=self.admin.username, password="Password123")
        form_data = {
            'tutor': self.tutor.id,
            'date': '2024-12-12',
            'day': 'thu',
            'start_time': self.lesson.start_time,
            'end_time': self.lesson.end_time,
            'time_of_day': 'morning',
            'topic': 'Test meeting',
            'status': 'scheduled',
            'notes': 'Test notes',
        }
        response = self.client.post(self.schedule_session_url, form_data, follow=True)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(Meeting.objects.count(), 1)
        meeting = Meeting.objects.first()
        self.assertEqual(meeting.student, self.student)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())  # Lesson request deleted

    def test_unsuccessful_when_errors(self):
        self.client.login(username=self.admin.username, password="Password123")
        form_data = {
            'start_time': '',
            'end_time': ''
        }
        response = self.client.post(self.schedule_session_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/schedule_session.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, MeetingForm))
        self.assertTrue(form.errors)