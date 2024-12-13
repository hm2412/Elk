from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from tutorials.models import TutorProfile
from django.contrib.messages.storage.fallback import FallbackStorage
from tutorials.views import TutorSubjectsView
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware

class TutorSubjectsFunctionViewTests(TestCase):
    fixtures = ['tutorials/tests/fixtures/other_users.json']

    def setUp(self):
        self.tutor_user = get_user_model().objects.get(username='@janedoe')
        self.url = reverse('tutor_subjects')

    def test_tutor_subjects_post_valid(self):
        self.client.login(username='@janedoe', password='Password123')
        data = {
            'subjects': ['Ruby', 'Swift']
        }
        response = self.client.post(self.url, data)
        tutor_profile = TutorProfile.objects.get(tutor=self.tutor_user)
        self.assertEqual(tutor_profile.subjects, ['Ruby', 'Swift'])
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Teaching subjects updated successfully')
        self.assertRedirects(response, reverse('dashboard'))

    def test_tutor_subjects_post_no_subjects(self):
        self.client.login(username='@janedoe', password='Password123')
        data = {
            'subjects': []
        }
        response = self.client.post(self.url, data)
        tutor_profile = TutorProfile.objects.get(tutor=self.tutor_user)
        self.assertEqual(tutor_profile.subjects, [])
        self.assertRedirects(response, reverse('dashboard'))

    def test_tutor_subjects_get_request(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard'))

    def test_tutor_subjects_not_logged_in(self):
        response = self.client.post(self.url, {'subjects': ['Ruby']})
        self.assertRedirects(response, reverse('log_in') + f'?next={self.url}')


class TutorSubjectsClassViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username='@janedoe', password='Password123')
        self.profile, _ = TutorProfile.objects.get_or_create(tutor=self.user, subjects=['Java', 'Ruby'])

    def test_get_initial(self):
        request = self.factory.get(reverse('tutor_subjects'))
        request.user = self.user
        view = TutorSubjectsView()
        view.setup(request)
        initial = view.get_initial()

        profile = TutorProfile.objects.get(tutor=self.user)
        self.assertEqual(initial['subjects'], profile.subjects)


    def test_form_valid_updates_profile(self):
        request = self.factory.post(reverse('tutor_subjects'), {
            'subjects': ['Java', 'Ruby', 'Python/Tensorflow']
        })
        request.user = self.user

        session_middleware = SessionMiddleware(get_response=lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        messages_middleware = MessageMiddleware(get_response=lambda req: None)
        messages_middleware.process_request(request)
        setattr(request, '_messages', FallbackStorage(request))

        view = TutorSubjectsView()
        view.setup(request)

        form = view.get_form_class()(data=request.POST)
        self.assertTrue(form.is_valid())

        response = view.form_valid(form)

        profile = TutorProfile.objects.get(tutor=self.user)

        self.assertEqual(profile.subjects, ['Java', 'Ruby', 'Python/Tensorflow'])
        self.assertEqual(response.status_code, 302) 
        self.assertEqual(response.url, reverse('dashboard'))


        messages = list(request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, 'Teaching subjects updated successfully.')
