from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.models import Meeting, TutorAvailability
from tutorials.calendar_utils import TutorCalendar
from datetime import datetime, date, time, timedelta

class TutorCalendarTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        
        self.tutor = self.User.objects.create_user(
            username='@janedoe',
            email='jane.doe@example.org',
            password='Password123',
            first_name='Jane',
            last_name='Doe',
            user_type='Tutor'
        )
        
        self.student = self.User.objects.create_user(
            username='@johndoe',
            email='john.doe@example.org',
            password='Password123',
            first_name='John',
            last_name='Doe',
            user_type='Student'
        )
    
    def create_test_meeting(self, meeting_date, start_time, end_time):
        """Helper method to create test meetings"""
        return Meeting.objects.create(
            tutor=self.tutor,
            student=self.student,
            date=meeting_date,
            day=meeting_date.strftime('%a').lower(),
            start_time=start_time,
            end_time=end_time,
            time_of_day='morning',
            topic='Python',
            status='scheduled',
            notes='Test meeting'
        )

    def test_calendar_init_with_default_values(self):
        """Test calendar initialization with default values"""
        calendar = TutorCalendar()
        today = datetime.now()
        self.assertEqual(calendar.year, today.year)
        self.assertEqual(calendar.month, today.month)

    def test_calendar_init_with_custom_values(self):
        """Test calendar initialization with custom values"""
        calendar = TutorCalendar(2024, 3)
        self.assertEqual(calendar.year, 2024)
        self.assertEqual(calendar.month, 3)

    def test_calendar_data_empty_month(self):
        """Test calendar generation with no meetings or availability"""
        calendar = TutorCalendar(2024, 3)
        data = calendar.get_calendar_data([], None)  # Test with None for meetings
        
        self.assertEqual(data['month_name'], 'March')
        self.assertEqual(data['year'], 2024)
        self.assertTrue(isinstance(data['weeks'], list))
        self.assertTrue(all('day' in day for week in data['weeks'] for day in week))

    def test_calendar_data_with_meetings(self):
        """Test calendar with multiple meetings"""
        calendar = TutorCalendar(2024, 3)
        meeting_date = date(2024, 3, 15)
        
        # Create two meetings on the same day
        meeting1 = self.create_test_meeting(meeting_date, time(9, 0), time(10, 0))
        meeting2 = self.create_test_meeting(meeting_date, time(11, 0), time(12, 0))
        
        data = calendar.get_calendar_data([], [meeting1, meeting2])
        
        # Find the day with meetings
        meetings_found = []
        for week in data['weeks']:
            for day in week:
                if day['day'] == 15:
                    meetings_found = day['meetings']
                    break
        
        self.assertEqual(len(meetings_found), 2)
        self.assertEqual(meetings_found[0]['start'], '09:00')
        self.assertEqual(meetings_found[1]['start'], '11:00')

    def test_calendar_navigation_data(self):
        """Test calendar navigation data for different months"""
        # Test December to January transition (forward)
        calendar = TutorCalendar(2024, 12)
        data = calendar.get_calendar_data([], [])
        self.assertEqual(data['next_month']['month'], 1)
        self.assertEqual(data['next_month']['year'], 2025)
        self.assertEqual(data['prev_month']['month'], 11)
        self.assertEqual(data['prev_month']['year'], 2024)

        # Test January to December transition (backward)
        calendar = TutorCalendar(2024, 1)
        data = calendar.get_calendar_data([], [])
        self.assertEqual(data['next_month']['month'], 2)
        self.assertEqual(data['next_month']['year'], 2024)
        self.assertEqual(data['prev_month']['month'], 12)
        self.assertEqual(data['prev_month']['year'], 2023)

    def test_calendar_today_highlight(self):
        """Test that today's date is properly highlighted"""
        today = datetime.now()
        calendar = TutorCalendar(today.year, today.month)
        data = calendar.get_calendar_data([], [])
        
        today_found = False
        for week in data['weeks']:
            for day in week:
                if day['day'] == today.day:
                    self.assertTrue(day['is_today'])
                    today_found = True
                    break
        
        self.assertTrue(today_found)

    def test_calendar_with_notes(self):
        """Test that meeting notes are properly included"""
        calendar = TutorCalendar(2024, 3)
        meeting_date = date(2024, 3, 15)
        meeting = self.create_test_meeting(meeting_date, time(9, 0), time(10, 0))
        meeting.notes = "Test meeting"
        meeting.save()
        
        data = calendar.get_calendar_data([], [meeting])
        
        meeting_found = False
        for week in data['weeks']:
            for day in week:
                if day['day'] == 15:
                    self.assertEqual(day['meetings'][0]['notes'], "Test meeting")
                    meeting_found = True
                    break
        
        self.assertTrue(meeting_found)

    def test_calendar_empty_notes(self):
        """Test handling of empty notes"""
        calendar = TutorCalendar(2024, 3)
        meeting_date = date(2024, 3, 15)
        meeting = self.create_test_meeting(meeting_date, time(9, 0), time(10, 0))
        meeting.notes = ""
        meeting.save()
        
        data = calendar.get_calendar_data([], [meeting])
        
        for week in data['weeks']:
            for day in week:
                if day['day'] == 15:
                    self.assertEqual(day['meetings'][0]['notes'], '')
