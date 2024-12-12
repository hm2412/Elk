from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from django.http import HttpResponse
from tutorials.tests.helpers import reverse_with_next, LogInTester, MenuTesterMixin

class ReverseWithNextTests(TestCase):
    def test_reverse_with_next(self):
        url_name = 'profile'
        next_url = '/dashboard/'
        expected_url = f"{reverse('profile')}?next=/dashboard/"
        self.assertEqual(reverse_with_next(url_name, next_url), expected_url)

    def test_reverse_with_next_invalid_input(self):
        with self.assertRaises(NoReverseMatch):
            reverse_with_next(None, '/dashboard/')

class LogInTesterTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_tester = LogInTester()
        self.login_tester.client = self.client

    def test_is_logged_in(self):
        # Test not logged in
        self.assertFalse(self.login_tester._is_logged_in())
        
        # Test logged in
        session = self.client.session
        session['_auth_user_id'] = '1'
        session.save()
        self.assertTrue(self.login_tester._is_logged_in())

class MenuTesterMixinTests(TestCase):
    def setUp(self):
        self.menu_tester = MenuTesterMixin()
        # Add TestCase's assertion methods to MenuTesterMixin instance
        self.menu_tester.assertHTML = self.assertInHTML
        self.menu_tester.assertNotHTML = lambda *args: not self.assertInHTML(*args)

    def test_assert_menu(self):
        html = """
            <nav>
                <a href="/password/">Password</a>
                <a href="/profile/">Profile</a>
                <a href="/log_out/">Logout</a>
            </nav>
        """
        response = HttpResponse(html)
        self.menu_tester.assert_menu(response)
        
        # Test missing menu
        response = HttpResponse("<div>No menu</div>")
        with self.assertRaises(AssertionError):
            self.menu_tester.assert_menu(response)

    def test_assert_no_menu(self):
        # Test when menu is absent
        response = HttpResponse("<div>No menu</div>")
        self.menu_tester.assert_no_menu(response)

        # Test when menu is present
        html = """
            <nav>
                <a href="/password/">Password</a>
                <a href="/profile/">Profile</a>
                <a href="/log_out/">Logout</a>
            </nav>
        """
        response = HttpResponse(html)
        with self.assertRaises(AssertionError):
            self.menu_tester.assert_no_menu(response)

    def test_menu_urls(self):
        expected_urls = [
            reverse('password'),
            reverse('profile'),
            reverse('log_out')
        ]
        self.assertEqual(self.menu_tester.menu_urls, expected_urls)
