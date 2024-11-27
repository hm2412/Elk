"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    user_type = forms.ChoiceField(
        choices = User.USER_TYPE,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
            user_type=self.cleaned_data.get('user_type'),
        )

        return user
    

from .models import Lesson 

class LessonRequestForm(forms.ModelForm):
    KNOWLEDGE_AREAS = [
        ('c++', 'C++'),
        ('scala', 'Scala'),
        ('java', 'Java'),
        ('python', 'Python'),
        ('ruby', 'Ruby'),
    ]
    TERMS = [
        ('sept-dec', 'September - December'),
        ('jan-april', 'January - April'),
        ('may-july', 'May - July'),
    ]
    VENUE_PREFERENCES = [
        ('online', 'Online'),
        ('onsite', 'Onsite'),
    ]
    DURATIONS    = [
        ('30', '30 min'),
        ('60', '60 min '),
        ('90', '90 min'),
        ('120', '120 min'),
    ]

    TIME_OF_DAY = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
    ]

    # Fields will now correspond to the model fields
    knowledge_area = forms.ChoiceField(choices=KNOWLEDGE_AREAS, label="Knowledge Area")
    term = forms.ChoiceField(choices=TERMS, label="Term")
    time_of_day = forms.ChoiceField(choices=TIME_OF_DAY, initial='morning', label="Preferred Time of Day")
    duration = forms.ChoiceField(choices=DURATIONS, label=" Duration")
    start_time = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        label="Preferred Start Time (HH:MM)"
    )
    days = forms.MultipleChoiceField(
        choices=[
            ('mon', 'Monday'),
            ('tue', 'Tuesday'),
            ('wed', 'Wednesday'),
            ('thu', 'Thursday'),
            ('fri', 'Friday'),
            ('sat', 'Saturday'),
            ('sun', 'Sunday'),
        ],
        widget=forms.CheckboxSelectMultiple,
        label="Days (select days)",
    )
    venue_preference = forms.ChoiceField(choices=VENUE_PREFERENCES, label="Venue Preference")

    class Meta:
        model = Lesson  # Connect the form to the LessonRequest model
        fields = ['knowledge_area', 'term', 'time_of_day', 'duration', 'start_time', 'days', 'venue_preference']