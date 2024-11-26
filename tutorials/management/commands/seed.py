from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from tutorials.models import User

import pytz
from faker import Faker
from random import randint, random, choice

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

    USER_COUNT = 300
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
    
    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()

        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        self.try_create_user({
            'username': username, 
            'email': email, 
            'first_name': first_name, 
            'last_name': last_name,
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
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
            user_type=group
        )
        
        # group = data.get('group', 'Student') # get the group or default to Student
        # user.user_type = group

        # if group in self.groups:
        #     user.groups.add(self.groups[group])
        #     if group == 'Admin':
        #         user.is_superuser = True
        #         user.is_staff = True
        #     elif group == 'Tutor':
        #         user.is_staff = True
        
        # user.save()
        # return user


        # if 'user_type' in data:
        #     group = self.groups[data['user_type']]
        #     user.groups.add(group)
        #     if group.name == 'Admin':
        #         user.is_superuser = True
        #         user.is_staff = True
        #         user.user_type = 'Admin'
        #     elif group.name == 'Tutor':
        #         user.is_staff = True
        #         user.user_type = 'Tutor'
        #     else:
        #         user.user_type = 'Student'

        #     user.save()
