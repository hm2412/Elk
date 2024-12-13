from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from django.utils import timezone
from tutorials.models import Meeting, TutorProfile, TutorAvailability, User, Lesson
from datetime import timedelta, datetime, time


import pytz
from faker import Faker

import random


user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe', 'group': 'Admin'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe', 'group': 'Tutor'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson', 'group': 'Student'},
]


def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'

def get_time_of_day(self, start_time):
        if time(8, 0) <= start_time < time(12, 0):
            return 'morning'
        if time(12, 0) <= start_time < time(16, 0):
            return 'afternoon'
        if time(16, 0) <= start_time < time(20, 0):
            return 'evening'

class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 300
    MEETING_COUNT = 10
    LESSON_COUNT = 10
    TUTOR_PROFILE_COUNT = 10
    TUTOR_AVAILABILITY_COUNT = 10
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.create_lessons()
        self.create_meetings()
        self.create_tutor_profiles()
        self.create_tutor_availabilities()
    
    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()
    
    def create_meetings(self):
        self.generate_meeting_fixture()
        self.generate_random_meetings()
    
    def create_lessons(self):
        self.generate_lesson_fixture()
        self.generate_random_lessons()

    def create_tutor_profiles(self):
        self.generate_tutor_profile_fixture()
        self.generate_random_tutor_profiles()

    def create_tutor_availabilities(self):
        self.generate_tutor_availability_fixture()
        self.generate_random_tutor_availbilities()

 # dont need to insert random allocation logic for user_fixtures, as they have default roles
    def generate_user_fixtures(self):
        for data in user_fixtures:

            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()

        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()

        print("User seeding complete.")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        
         #  randomly assign a user types from the list based on the probabilities of each
        user_types = ['Student', 'Tutor', 'Admin']
        probabilities = [0.80, 0.15, 0.05] 
        #return a single user_type and get the first element in the list to be stored in user_type 
        user_type = random.choices(user_types, weights=probabilities, k=1)[0] 

        self.try_create_user({
            'username': username, 
            'email': email, 
            'first_name': first_name, 
            'last_name': last_name,
            'group': user_type 

        })

    def try_create_user(self, data):
        try:
            if User.objects.filter(username=data['username']).exists():
                print('User already exists')
                return
            if User.objects.filter(email=data['email']).exists():
                print('Email already exists')
                return

            self.create_user(data)
        except Exception as e:
            print(f'Failed to create user: {data} with error message: {e}')

    def create_user(self, data):

        group = data.get('group', 'Student')
        group_instance, created = Group.objects.get_or_create(name=group)
       
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
            user_type=group
        )
        
        user.groups.add(group_instance)

    """ Seeding Meetings """

    def generate_meeting_fixture(self):
        tutor = User.objects.get(username='@janedoe')
        student = User.objects.get(username='@charlie')

        data = {
            'tutor': tutor,
            'student': student,
            'date': datetime.now().date(),
            'day': "mon",
            'start_time': "10:00:00",
            'end_time': "11:00:00",
            'time_of_day': "morning",
            'topic': "Python",
            'status': "scheduled",
            'notes': "Some notes"
        }

        self.try_create_meeting(data)

    def generate_random_meetings(self):
        count = Meeting.objects.count()

        while count < self.MEETING_COUNT:
            print(f"Seeding meeting {count}/{self.MEETING_COUNT}", end='\r')
            self.generate_meeting()
            count = Meeting.objects.count()
        print("Meeting seeding complete.")

    def generate_meeting(self):

        tutors = User.objects.filter(user_type='Tutor')
        students = User.objects.filter(user_type='Student')
        topics = ['C++', 'Scala', 'Java', 'Python', 'Ruby']
        tutor = random.choice(tutors)
        student = random.choice(students)

        start_time = time(random.randint(8, 19), random.choice([0, 15, 30, 45]))
        start_datetime = datetime.combine(self.faker.date_this_month(), start_time)
        date = start_datetime.date()
        day = start_datetime.strftime('%a').lower()
        end_time = (datetime.combine(datetime.today(), start_time) + timedelta(hours=1)).time()
        time_of_day = self.get_time_of_day(start_time)

        topic = random.choice(topics)
        status = "scheduled"
        notes = self.faker.sentence()

        self.try_create_meeting({
            'tutor': tutor,
            'student': student,
            'date': date,
            'day': day,
            'start_time': start_time,
            'end_time': end_time,
            'time_of_day': time_of_day,
            'topic': topic,
            'status': status,
            'notes': notes
        })

    def try_create_meeting(self, data):
        try:
            existing_meetings = Meeting.objects.filter(
                tutor=data['tutor'],
                date=data['date'],
                start_time=data['start_time'],
                end_time=data['end_time']
            )
            if existing_meetings.exists():
                print('Meeting already exists')
                return 

            Meeting.objects.create(
                tutor=data['tutor'],
                student=data['student'],
                date=data['date'],
                day=data['day'],
                start_time=data['start_time'],
                end_time=data['end_time'],
                time_of_day=data['time_of_day'],
                topic=data['topic'],
                status=['status'],
                notes=data['notes']
            )

        except Exception as e:
            print(f"Failed to create meeting: {e}")
            return False

    def get_time_of_day(self, start_time):
        if time(8, 0) <= start_time < time(12, 0):
            return 'morning'
        if time(12, 0) <= start_time < time(16, 0):
            return 'afternoon'
        if time(16, 0) <= start_time < time(20, 0):
            return 'evening'

    
    """ Seeding Lesson Requests """

    def generate_lesson_fixture(self):
        student = User.objects.get(username='@charlie')

        data = {
            'student': student,
            'knowledge_area': 'python',
            'term': 'sept-dec',
            'start_time': time(10, 0),
            'duration': 60,
            'end_time': time(11, 0),
            'days': ['mon', 'wed', 'fri'],
            'time_of_day': 'morning',
            'venue_preference': 'online',
            'approved': True,
            'created_at': timezone.make_aware(datetime(2024, 9, 1, 9, 30))
        }

        self.try_create_lesson(data)

    def generate_random_lessons(self):
        count = Lesson.objects.count()

        while count < self.LESSON_COUNT:
            print(f"Seeding lesson {count}/{self.LESSON_COUNT}", end='\r')
            self.generate_lesson()
            count = Lesson.objects.count()
        print("Lesson seeding complete.")

    def generate_lesson(self):
        students = User.objects.filter(user_type='Student')

        if not students.exists(): 
            print("No students found. Skipping lesson generation.")
            return
        
        knowledge_areas = [choice[0] for choice in Lesson.KNOWLEDGE_AREAS]
        terms = [choice[0] for choice in Lesson.TERMS]
        durations = [choice[0] for choice in Lesson.DURATIONS]
        venue_preferences = [choice[0] for choice in Lesson.VENUE_PREFERENCES]
        days = [choice[0] for choice in Lesson.DAY_CHOICES]

        student = random.choice(students)
        knowledge_area = random.choice(knowledge_areas)
        term = random.choice(terms)
        start_time = time(random.randint(8, 19), random.choice([0, 15, 30, 45]))
        start_datetime = datetime.combine(self.faker.date_this_month(), start_time)
        duration = random.choice(durations)
        end_time = (start_datetime + timedelta(minutes=duration)).time()
        days = random.sample(days, k=random.randint(1, 3))
        time_of_day=self.get_time_of_day(start_time)
        venue_preference = random.choice(venue_preferences)
        approved = random.choice([True, False])
        created_at = timezone.make_aware(self.faker.date_time_between(start_date='-10m', end_date='-1m'))

        self.try_create_lesson({
            'student': student,
            'knowledge_area': knowledge_area,
            'term': term,
            'start_time': start_time,
            'duration': duration,
            'end_time': end_time,
            'days': days,
            'time_of_day': time_of_day,
            'venue_preference': venue_preference,
            'approved': approved,
            'created_at': created_at
        })

    def try_create_lesson(self, data):
        try:
            existing_lessons = Lesson.objects.filter(
                student=data['student'],
                knowledge_area=data['knowledge_area'],
                term=data['term'],
                start_time=data['start_time'],
                duration=data['duration'],
                end_time=data['end_time'],
                days=data['days'],
                time_of_day=data['time_of_day'],
                venue_preference=data['venue_preference'],
                approved=data['approved'],
                created_at=data['created_at']
            )

            if existing_lessons.exists():
                print('Lessons already exists')
                return 

            Lesson.objects.create(
                student=data['student'],
                knowledge_area=data['knowledge_area'],
                term=data['term'],
                start_time=data['start_time'],
                duration=data['duration'],
                end_time=data['end_time'],
                days=data['days'],
                time_of_day=data['time_of_day'],
                venue_preference=data['venue_preference'],
                approved=data['approved'],
                created_at=data['created_at']
            )

        except Exception as e:
            print(f"Failed to create lesson: {data} with error message: {e}")


    """ Seeder for Tutor Profiles"""
    def generate_tutor_profile_fixture(self):
        tutor = User.objects.get(username='@janedoe')

        data = {
                'tutor': tutor,
                'hourly_rate': 30,
                'subjects': ['C++', 'Python']
            }
        self.try_create_tutor_profile(data)
        
    def generate_random_tutor_profiles(self):
        count = TutorProfile.objects.count()

        while count < self.TUTOR_PROFILE_COUNT:
            print(f"Seeding tutor profile {count}/{self.TUTOR_PROFILE_COUNT}", end='\r')
            self.generate_tutor_profile()
            count = TutorProfile.objects.count()
        print("Tutor profile seeding complete.")

    def generate_tutor_profile(self):
        tutors = User.objects.filter(user_type='Tutor').exclude(tutor_profile__isnull=False)

        if not tutors.exists():
            print("No tutos found. Skipping profile generation.")
            return
    
        subjects_list = ['C++', 'Scala', 'Java', 'Python', 'Ruby']

        tutor = random.choice(tutors)
        hourly_rate = round(random.uniform(20, 100), 2)
        subjects = random.sample(subjects_list, k=random.randint(1, len(subjects_list)))

        self.try_create_tutor_profile({
                'tutor': tutor,
                'hourly_rate': hourly_rate,
                'subjects': subjects
        })

    def try_create_tutor_profile(self, data):
        try:
            if TutorProfile.objects.filter(tutor=data['tutor']).exists():
                print('Tutor Profile already exists')
                return

            TutorProfile.objects.create(
                tutor=data['tutor'],
                hourly_rate=data['hourly_rate'],
                subjects=data['subjects']
        )
        except Exception as e:
            print(f"Failed to create tutor profile: {e}")

    """ Seeder for Tutor Availability"""

    def generate_tutor_availability_fixture(self):
        tutor = User.objects.get(username='@janedoe')

        data = {
                'tutor': tutor,
                'day': 'Tuesday',
                'start_time': '14:00:00',
                'end_time': '17:00:00',
                'is_available': True
            }
        
        self.try_create_tutor_availability(data)

    def generate_random_tutor_availbilities(self):
        count = TutorAvailability.objects.count()

        while count < self.TUTOR_AVAILABILITY_COUNT:
            print(f"Seeding tutor availability {count}/{self.TUTOR_AVAILABILITY_COUNT}", end='\r')
            self.generate_tutor_availability()
            count = TutorAvailability.objects.count()
        print("Tutor availability seeding complete.")

    def generate_tutor_availability(self):
        tutors = User.objects.filter(user_type='Tutor')
        days = [choice[0] for choice in TutorAvailability.DAYS_OF_WEEK]

        tutor = random.choice(tutors)
        day = random.choice(days)
        start_time = datetime.strptime(f"{random.randint(8, 19)}:{random.choice([0, 15, 30, 45]):02}", "%H:%M")
        end_time = (start_time + timedelta(hours=1)).time()
        is_available = random.choice([True, False])

        self.try_create_tutor_availability({
            'tutor': tutor, 
            'day': day,
            'start_time': start_time,
            'end_time': end_time,
            'is_available': is_available
        })


    def try_create_tutor_availability(self, data):
        try:
            existing_availabilities = TutorAvailability.objects.filter(
                tutor=data['tutor'],
                start_time=data['start_time'],
                end_time=data['end_time'],
                day=data['day'],
                is_available=data['is_available']
            )

            if existing_availabilities.exists():
                print(f"Availability already exists for {data['tutor']} on {data['day']}")
                return

            TutorAvailability.objects.create(
                tutor=data['tutor'],
                day=data['day'],
                start_time=data['start_time'],
                end_time=data['end_time'],
                is_available=data['is_available']
            )
        except Exception as e:
            print(f"Failed to create tutor availability: {e}")