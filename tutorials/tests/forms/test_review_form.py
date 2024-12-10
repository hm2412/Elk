from django.test import TestCase
from django import forms
from tutorials.forms import ReviewForm
from tutorials.models import Review, User
from django.contrib.auth import get_user_model

class ReviewFormTestCase(TestCase):
    def test_form_field(self):
        form = ReviewForm()
        self.assertIn("content", form.fields)
        content_field = form.fields["content"]
        self.assertTrue(isinstance(content_field, forms.CharField))
        self.assertIn("rating", form.fields)
        rating = form.fields["rating"]
        self.assertTrue(isinstance(rating, forms.FloatField))


    def test_valid_form(self):
        """Test the form with valid data"""
        # Data for a valid form submission
        data = {
            'rating': 4.5,
            'content': 'This is a valid review content.'
        }
        
        # Create the form with the given data
        form = ReviewForm(data=data)
        
        # Check if the form is valid
        self.assertTrue(form.is_valid())

        review = form.save(commit=False)
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.content, 'This is a valid review content.')
        
    def test_invalid_rating_too_low(self):
        """Test the form with an invalid rating (too low)"""
        data = {
            'rating': -1,
            'content': 'This review has an invalid rating.'
        }
        
        # Create the form with the given data
        form = ReviewForm(data=data)
        
        # Check if the form is invalid
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)
        
    def test_invalid_rating_too_high(self):
        """Test the form with an invalid rating (too high)"""
        # Data for an invalid form submission (rating greater than 5)
        data = {
            'rating': 6,
            'content': 'This review has an invalid rating.'
        }
        
        # Create the form with the given data
        form = ReviewForm(data=data)
        
        # Check if the form is invalid
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)
        
    def test_invalid_content_too_long(self):
        """Test the form with invalid content (exceeds max length)"""
        # Data for an invalid form submission (content too long)
        data = {
            'rating': 4,
            'content': 'A' * 91  # 91 characters, exceeds max length of 90
        }
        
        # Create the form with the given data
        form = ReviewForm(data=data)
        
        # Check if the form is invalid
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    
    def test_save_method(self):
        # Create a user (student)
        user = get_user_model().objects.create_user(
            username='@studentuser',
            first_name='John',
            last_name='Doe',
            email='student@example.com',
            password='password123',
            user_type='Student'  # Set user_type to 'Student'
        )
        
        # Create valid form data
        form_data = {
            'content': 'Great lesson!',
            'rating': 5
        }
        
        # Create the form with the user instance
        form = ReviewForm(data=form_data)
        form.user = user  # Manually attach the user to the form

        # Check if the form is valid
        self.assertTrue(form.is_valid())

        # Save the review and check the database for the new review
        form.save(commit=True)
        
        # Count the number of reviews in the database
        review_count = Review.objects.count()
        
        # Ensure that the review count increased by 1
        self.assertEqual(review_count, 1)
        
        # Check if the review's student is correctly assigned
        review = Review.objects.first()
        self.assertEqual(review.student, user)

