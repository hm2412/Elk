
from .mixins import LoginProhibitedMixin
from django.views.generic import TemplateView
from .mixins import LoginProhibitedMixin
from django.shortcuts import reverse

class Home(LoginProhibitedMixin, TemplateView):
    """Display the application's start/home screen."""
    template_name = 'home.html'

    def get_redirect_when_logged_in_url(self):
        return reverse('dashboard')
