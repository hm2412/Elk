from django.test import TestCase
from django.urls import reverse
from tutorials.forms import ReviewForm
from django.contrib.auth import get_user_model
from tutorials.models import Review

class ReviewViewTest(TestCase):
    
    def setUp(self):

        self.user = get_user_model().objects.create_user(
            username='@testuser',
            first_name='Test',
            last_name='User',
            email='testuser@example.com',
            password='testpassword',
            user_type='Student'
        )
        

        self.client.login(username='@testuser', password='testpassword')
        

        self.form_data = {
            'content': 'Great tutorial!',
            'rating': 4
        }


        self.url = reverse('submit_review')


        response = self.client.post(self.url, self.form_data)

        self.review = Review.objects.get(content='Great tutorial!', rating=4)

    def test_create_book_url(self):

        self.assertEqual(self.url, '/submit_review/')

    def test_get_create_book(self):

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review.html')
        self.assertIn("review", response.context)
        form = response.context["review"]
        self.assertTrue(isinstance(form, ReviewForm)) 
        self.assertFalse(form.is_bound) 

    def test_review_post_in_setUp(self):

        self.assertTrue(Review.objects.filter(content='Great tutorial!', rating=4).exists())
        self.assertEqual(self.review.student.username, '@testuser')

    def test_redirect_after_valid_submission(self):

        response = self.client.post(self.url, self.form_data)


        self.assertEqual(response.status_code, 302)


        self.assertRedirects(response, self.url)

        from django.contrib.messages import get_messages
        storage = get_messages(response.wsgi_request)
        message = list(storage)[0]  # Get the first message
        self.assertEqual(message.message, 'Thank you for your feedback!')

    def test_invalid_form_submission(self):
        invalid_form_data = {
            'content': '',
            'rating': 4
        }
        response = self.client.post(self.url, invalid_form_data)

        self.assertEqual(response.status_code, 200)
        
        self.assertIn("review", response.context)
        form = response.context["review"]
        
        self.assertTrue(form.errors)

    def test_review_association_with_user(self):
        review = Review.objects.get(content='Great tutorial!')
        self.assertEqual(review.student.username, '@testuser')
    
    def test_success_message_displayed(self):
        response = self.client.post(self.url, self.form_data)

        self.assertEqual(response.status_code, 302)

        from django.contrib.messages import get_messages
        storage = get_messages(response.wsgi_request)
        message = list(storage)[0]
        self.assertEqual(message.message, 'Thank you for your feedback!')

