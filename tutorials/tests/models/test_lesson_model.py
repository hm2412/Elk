from django.test import TestCase
from django.utils import timezone
from datetime import datetime, time, timedelta  
from tutorials.models import Lesson
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError 

class LessonModelTestCase(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = get_user_model().objects.get(username='@charlie')

    def test_lesson_save_sets_end_time_and_time_of_day(self):
        lesson = Lesson(
            student=self.user,
            knowledge_area='Python',
            term='Sept-Dec',
            start_time=time(9, 30),
            duration=90,
            days=["mon", "wed"],
            venue_preference='online'
        )
        lesson.save()
        expected_end_time = (
            timezone.make_aware(datetime.combine(datetime.today(), lesson.start_time))
            + timedelta(minutes=lesson.duration)
        ).time()
        self.assertEqual(lesson.end_time, expected_end_time)
        self.assertEqual(lesson.time_of_day, 'morning')

    def test_lesson_save_without_start_time(self):
        lesson = Lesson(
            student=self.user,
            knowledge_area='Python',
            term='Sept-Dec',
            start_time=None,  
            duration=90,
            days=["mon", "wed"],
            venue_preference='online'
        )
        lesson.save()
        self.assertIsNone(lesson.end_time)  

    def test_lesson_save_without_duration(self):
        with self.assertRaises(IntegrityError):
            Lesson.objects.create(
                student=self.user,
                knowledge_area='Python',
                term='Sept-Dec',
                start_time=time(9, 30),
                duration=None,  
                days=["mon", "wed"],
                venue_preference='online'
            )
    def test_get_time_of_day_for_different_times(self):
    
        lesson_morning = Lesson(
            student=self.user,
            knowledge_area='Java',
            term='Sept-Dec',
            start_time=time(9, 0),  
            duration=60,
            days=["mon", "wed"],
            venue_preference='online'
        )
        self.assertEqual(lesson_morning.get_time_of_day(), 'morning')

        lesson_afternoon = Lesson(
            student=self.user,
            knowledge_area='Scala',
            term='Sept-Dec',
            start_time=time(14, 0),  
            duration=60,
            days=["mon", "wed"],
            venue_preference='onsite'
        )
        self.assertEqual(lesson_afternoon.get_time_of_day(), 'afternoon')

        lesson_evening = Lesson(
            student=self.user,
            knowledge_area='Ruby',
            term='Jan-April',
            start_time=time(17, 30), 
            duration=60,
            days=["tue", "thu"],
            venue_preference='onsite'
        )
        self.assertEqual(lesson_evening.get_time_of_day(), 'evening')

        lesson_evening = Lesson(
            student=self.user,
            knowledge_area='Ruby',
            term='Jan-April',
            start_time=time(21, 30), 
            duration=60,
            days=["tue", "thu"],
            venue_preference='onsite'
        )
        self.assertNotEqual(lesson_evening.get_time_of_day(), 'evening')

    def test_lesson_str_method(self):
        lesson = Lesson(
            student=self.user,
            knowledge_area='Python',
            term='Sept-Dec',
            start_time=time(9, 0),
            duration=60,
            days=["mon", "wed"],
            venue_preference='online'
        )
        expected_str = f"{self.user}'s request for Python tutoring"
        self.assertEqual(str(lesson), expected_str)
        
    def test_time_range_method(self):
        
        lesson = Lesson(
            student=self.user,
            knowledge_area='python',
            term='sept-dec',
            start_time=time(10, 0),  
            duration=60,  
            days=["mon", "wed"],
            venue_preference='online'
        )
        lesson.save()
        expected_time_range = "10:00 - 11:00"  
        self.assertEqual(lesson.time_range(), expected_time_range)

        lesson_no_times = Lesson(
            student=self.user,
            knowledge_area='python',
            term='sept-dec',
            duration=60,
            days=["mon", "wed"],
            venue_preference='online'
        )
        self.assertEqual(lesson_no_times.time_range(), "No time set")

    def test_formatted_days_method(self):
        lesson = Lesson(
            student=self.user,
            knowledge_area='python',
            term='sept-dec',
            start_time=time(10, 0),
            duration=60,
            days=["mon", "wed", "fri"],  
            venue_preference='online'
        )
        expected_formatted_days = "Monday, Wednesday, Friday"
        self.assertEqual(lesson.formatted_days(), expected_formatted_days)