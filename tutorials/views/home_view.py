
from .mixins import LoginProhibitedMixin
from django.views.generic import TemplateView
from .mixins import LoginProhibitedMixin
from django.shortcuts import reverse, render
from tutorials.helpers import login_prohibited


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')