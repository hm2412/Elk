from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from tutorials.models import User, Meeting
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

class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 500
    MEETING_COUNT = 300
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.create_meetings()
    
    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()
    
    def create_meetings(self):
        self.generate_meeting_fixture()
        self.generate_random_meetings()

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
        #return a single user_type andget the first element in the list to be stored in user_type 
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
            'notes': "Please remember this meeting."
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

        start_time = time(random.randint(8, 19), 0, 0)

        start_datetime = datetime.combine(self.faker.date_this_month(), start_time)

        tutor = random.choice(tutors)
        student = random.choice(students)
        date = start_datetime.date()
        day = start_datetime.strftime('%a').lower()
        end_time = (datetime.combine(datetime.today(), start_time) + timedelta(hours=1)).time()
        time_of_day=self.get_time_of_day(start_time)
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
    
            if Meeting.objects.filter(
                tutor=data['tutor'],
                student=data['student'],
                date=data['date'],
                start_time=data['start_time'],
                topic=data['topic']
            ).exists():
                print("Meeting already exists")
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
            status=data['status'],
            notes=data.get('notes', '')
        )

        except Exception as e:
            print(f"Failed to create meeting: {data} with error message: {e}")

    def get_time_of_day(self, start_time):
        if time(8, 0) <= start_time < time(12, 0):
            return 'morning'
        if time(12, 0) <= start_time < time(16, 0):
            return 'afternoon'
        if time(16, 0) <= start_time < time(20, 0):
            return 'evening'