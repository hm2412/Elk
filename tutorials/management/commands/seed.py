from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from tutorials.models import User

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

    USER_COUNT = 600
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
        print("User seeding complete.      ")

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
