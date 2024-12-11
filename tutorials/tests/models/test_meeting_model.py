from django.test import TestCase
from datetime import time
from tutorials.models import Meeting
from django.contrib.auth import get_user_model


class MeetingModelTestCase(TestCase):

    def setUp(self):
        self.User = get_user_model()

        #tutor
        self.tutor = self.User.objects.create_user(
            username='@janedoe',
            email='jane.doe@example.org',
            password='Password123',
            user_type='Tutor'
        )

        # student 
        self.student = self.User.objects.create_user(
            username='@charlie',
            email='charlie.johnson@example.org',
            password='Password123',
            user_type='Student'
        )

    def test_meeting_str_method(self):
       
        meeting = Meeting(
            tutor=self.tutor,
            student=self.student,
            date='2024-12-15',
            day='mon',
            start_time=time(10, 0),
            end_time=time(11, 0),
            time_of_day='morning',
            topic='Java'
        )

        expected_str = f"Meeting: {self.tutor.username} with {self.student.username} on 2024-12-15"
        self.assertEqual(str(meeting), expected_str)

    def test_time_range_method(self):
      
        meeting = Meeting(
            tutor=self.tutor,
            student=self.student,
            date='2024-12-15',
            day='mon',
            start_time=time(10, 0),
            end_time=time(11, 0),
            time_of_day='morning',
            topic='Java'
        )

        expected_time_range = "10:00 - 11:00"
        self.assertEqual(meeting.time_range(), expected_time_range)

    def test_meeting_save_creates_correct_time_of_day(self):
        
        meeting_morning = Meeting(
            tutor=self.tutor,
            student=self.student,
            date='2024-12-15',
            day='mon',
            start_time=time(9, 0),
            end_time=time(10, 0),
            time_of_day='morning',
            topic='Java'
        )

        meeting_morning.save()
        self.assertEqual(meeting_morning.time_of_day, 'morning')

        meeting_afternoon = Meeting(
            tutor=self.tutor,
            student=self.student,
            date='2024-12-15',
            day='mon',
            start_time=time(14, 0),
            end_time=time(15, 0),
            time_of_day='afternoon',
            topic='Java'
        )

        meeting_afternoon.save()
        self.assertEqual(meeting_afternoon.time_of_day, 'afternoon')

        meeting_evening = Meeting(
            tutor=self.tutor,
            student=self.student,
            date='2024-12-15',
            day='mon',
            start_time=time(17, 30),
            end_time=time(18, 30),
            time_of_day='evening',
            topic='Java'
        )

        meeting_evening.save()
        self.assertEqual(meeting_evening.time_of_day, 'evening')