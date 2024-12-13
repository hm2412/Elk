
from .mixins import LoginProhibitedMixin
from django.views.generic import TemplateView
from .mixins import LoginProhibitedMixin

class Home(LoginProhibitedMixin, TemplateView):
    """Display the application's start/home screen."""
    template_name = 'home.html'
