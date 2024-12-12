from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import Review
from tutorials.forms import ReviewForm

class ReviewViewTest(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = get_user_model().objects.get(username='@charlie')
        self.client.login(username='@charlie', password='Password123')

        self.form_data = {
            'content': 'Great tutorial!',
            'rating': 4
        }

        self.url = reverse('submit_review')

    def test_create_review_url(self):
        self.assertEqual(self.url, '/submit_review/')

    def test_get_create_review(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review.html')
        self.assertIn("review", response.context)
        form = response.context["review"]
        self.assertTrue(isinstance(form, ReviewForm))
        self.assertFalse(form.is_bound)

    def test_review_view_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('log_in') + f'?next={self.url}')

    def test_review_post_in_setUp(self):
        self.client.post(self.url, self.form_data)
        self.assertTrue(Review.objects.filter(content='Great tutorial!', rating=4).exists())
        review = Review.objects.get(content='Great tutorial!', rating=4)
        self.assertEqual(review.student.username, '@charlie')

    def test_redirect_after_valid_submission(self):
        response = self.client.post(self.url, self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        storage = get_messages(response.wsgi_request)
        message = list(storage)[0]  # Get the first message
        self.assertEqual(message.message, 'Thank you for your feedback!')

    def test_review_association_with_user(self):
        self.client.post(self.url, self.form_data)
        review = Review.objects.get(content='Great tutorial!')
        self.assertEqual(review.student.username, '@charlie')

    def test_success_message_displayed(self):
        response = self.client.post(self.url, self.form_data)
        self.assertEqual(response.status_code, 302)
        storage = get_messages(response.wsgi_request)
        message = list(storage)[0]
        self.assertEqual(message.message, 'Thank you for your feedback!')

    def test_review_empty_content(self):
        invalid_form_data = {
            'content': '',
            'rating': 4
        }
        response = self.client.post(self.url, invalid_form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review.html')
        self.assertIn("review", response.context)
        form = response.context["review"]
        self.assertTrue(form.errors)

    def test_review_invalid_rating(self):
        invalid_form_data = {
            'content': 'Great tutorial!',
            'rating': 6
        }
        response = self.client.post(self.url, invalid_form_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("review", response.context)
        form = response.context["review"]
        self.assertTrue(form.errors)
