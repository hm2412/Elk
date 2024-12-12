from django.test import TestCase
from tutorials.models import User, Meeting
from tutorials.helpers import (
    get_students_for_tutor,
    get_all_students,
    annotate_students_with_tutors,
    get_all_tutors,
    filter_tutors_by_subjects,
    annotate_tutors_with_availability
)

class GetStudentsForTutorTests(TestCase):
    fixtures = ['tutorials/fixtures/test_meetings.json', 
                'tutorials/tests/fixtures/other_users.json']
    
    def setUp(self):
        self.tutor = User.objects.get(username="@janedoe") 
        self.student1 = User.objects.get(username="@charlie") 
        self.student2 = User.objects.get(username="@mikemiles") 

    def test_get_students_for_tutor(self):
        students = get_students_for_tutor(self.tutor)
        self.assertEqual(students.count(), 2)
        self.assertIn(self.student1, students)
        self.assertIn(self.student2, students)

class GetAllStudentsTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']
    
    def setUp(self):
        self.non_student = User.objects.get(username="@janedoe") 
        self.student1 = User.objects.get(username="@charlie") 
        self.student2 = User.objects.get(username="@mikemiles") 

    def test_get_all_students(self):
        students = get_all_students()
        self.assertEqual(students.count(), 2)
        self.assertIn(self.student1, students)
        self.assertIn(self.student2, students)
        self.assertNotIn(self.non_student, students)

class AnnotateStudentsWithTutorsTests(TestCase):
    fixtures = ['tutorials/fixtures/test_meetings.json', 
                'tutorials/tests/fixtures/other_users.json']
    
    def setUp(self):
        self.tutor = User.objects.get(username="@janedoe") 
        self.student1 = User.objects.get(username="@charlie") 
        self.student2 = User.objects.get(username="@mikemiles") 

    def test_annotate_students_with_tutors(self):
        users = [self.student1, self.student2]
        annotate_students_with_tutors(users)
        
        self.assertTrue(hasattr(self.student1, 'current_tutors'))
        self.assertEqual(self.student1.current_tutors, [self.tutor.username])
        self.assertTrue(hasattr(self.student2, 'current_tutors'))
        self.assertEqual(self.student2.current_tutors, [self.tutor.username])

class GetAllTutorsTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.tutor1 = User.objects.get(username="@janedoe") 
        self.tutor2 = User.objects.get(username="@leslielowe") 
        self.student = User.objects.get(username="@charlie") 

    def test_get_all_tutors(self):
        tutors = get_all_tutors()
        self.assertEqual(tutors.count(), 2)
        self.assertIn(self.tutor1, tutors)
        self.assertIn(self.tutor2, tutors)
        self.assertNotIn(self.student, tutors)


class FilterTutorsBySubjectsTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json',
                'tutorials/tests/fixtures/tutor_profile.json']

    def setUp(self):
        self.tutor1 = User.objects.get(username="@janedoe") 
        self.tutor2 = User.objects.get(username="@leslielowe") 

    def test_filter_tutors_by_subjects(self):
        subject_filters = ['ruby']
        tutors = filter_tutors_by_subjects([self.tutor1, self.tutor2], subject_filters)
        self.assertEqual(len(tutors), 1)
        self.assertIn(self.tutor2, tutors)
        self.assertNotIn(self.tutor1, tutors)

class AnnotateTutorsWithAvailabilityTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json',
                'tutorials/tests/fixtures/tutor_availability.json']
    
    def setUp(self):
        self.tutor1 = User.objects.get(username="@janedoe") 
        self.tutor2 = User.objects.get(username="@leslielowe") 

    def test_annotate_tutors_with_availability(self):
        tutors = [self.tutor1, self.tutor2]
        annotate_tutors_with_availability(tutors)
        
        self.assertTrue(hasattr(self.tutor1, 'availability'))
        self.assertEqual(self.tutor1.availability.count(), 1)
        
        self.assertTrue(hasattr(self.tutor2, 'availability'))
        self.assertEqual(self.tutor2.availability.count(), 1)
