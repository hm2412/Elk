from django.test import TestCase
from datetime import time
from tutorials.models import Meeting
from django.contrib.auth import get_user_model

class MeetingModelTestCase(TestCase):
    fixtures = [
        'tutorials/tests/fixtures/other_users.json', 
        'tutorials/fixtures/test_meetings.json'  
    ]

    def setUp(self):
        self.User = get_user_model()
        self.tutor = self.User.objects.get(username='@janedoe')
        self.student = self.User.objects.get(username='@charlie')

    def test_meeting_str_method(self):
        meeting = Meeting.objects.get(pk=1)  
        expected_str = f"Meeting: {meeting.tutor.username} with {meeting.student.username} on {meeting.date}"
        self.assertEqual(str(meeting), expected_str)

    def test_time_range_method(self):
        meeting = Meeting.objects.get(pk=1) 
        expected_time_range = "14:00 - 15:00"
        self.assertEqual(meeting.time_range(), expected_time_range)

    def test_meeting_save_creates_correct_time_of_day(self):
        meeting_morning = Meeting.objects.create(
            tutor=self.tutor,
            student=self.student,
            date='2024-12-15',
            day='mon',
            start_time=time(9, 0),
            end_time=time(10, 0),
            time_of_day='morning',
            topic='Java'
        )
        self.assertEqual(meeting_morning.time_of_day, 'morning')

        meeting_afternoon = Meeting.objects.create(
            tutor=self.tutor,
            student=self.student,
            date='2024-12-15',
            day='mon',
            start_time=time(14, 0),
            end_time=time(15, 0),
            time_of_day='afternoon',
            topic='Java'
        )
        self.assertEqual(meeting_afternoon.time_of_day, 'afternoon')

        meeting_evening = Meeting.objects.create(
            tutor=self.tutor,
            student=self.student,
            date='2024-12-15',
            day='mon',
            start_time=time(17, 30),
            end_time=time(18, 30),
            time_of_day='evening',
            topic='Java'
        )
        self.assertEqual(meeting_evening.time_of_day, 'evening')
