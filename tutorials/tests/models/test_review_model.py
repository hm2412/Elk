from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import Review

class ReviewTestCase(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = get_user_model().objects.get(username='@charlie')

        content = 'This is a valid good website content.'
        review_text = 'This is a valid review text.'
        rating = 4
        self.review = Review(content=content, review_text=review_text, rating=rating, student=self.user)

        self.valid_review_data = {
            "content": "This is a valid content.",
            "review_text": "This is a valid review text.",
            "rating": 4,
            "student": self.user,
        }

    def create_review(self, **kwargs):
        data = self.valid_review_data.copy()  
        data.update(kwargs)  
        return Review(**data)

    def test_valid_review_is_valid(self):
        try:
            self.review.full_clean()
        except ValidationError:
            self.fail("Review is not valid")

    def test_invalid_review_is_invalid(self):
        self.review.content = ""
        with self.assertRaises(ValidationError):
            self.review.full_clean()

    def test_missing_review_text_is_invalid(self):
        self.review.review_text = ""
        with self.assertRaises(ValidationError):
            self.review.full_clean()

    def test_invalid_rating_value(self):
        self.review.rating = 6 
        with self.assertRaises(ValidationError):
            self.review.full_clean()

    def test_invalid_rating_type(self):
        self.review.rating = "good"
        with self.assertRaises(ValidationError):
            self.review.full_clean()

    def test_missing_student_is_invalid(self):
        self.review.student = None
        with self.assertRaises(ValidationError):
            self.review.full_clean()

    def test_missing_content_is_invalid(self):
        self.review.content = ""
        with self.assertRaises(ValidationError):
            self.review.full_clean()

    def test_missing_user_is_invalid(self):
        self.review.student = None 
        with self.assertRaises(ValidationError):
            self.review.full_clean()

    def test_rating_below_minimum_is_invalid(self):
        self.review.rating = 0 
        with self.assertRaises(ValidationError):
            self.review.full_clean()

    def test_rating_above_maximum_is_invalid(self):
        self.review.rating = 6 
        with self.assertRaises(ValidationError):
            self.review.full_clean()

    def test_str_method(self):
            review = self.create_review()
            expected_str = f"Review by {self.user.username} (Rating: 4)"
            self.assertEqual(str(review), expected_str)