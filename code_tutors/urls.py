"""
URL configuration for code_tutors project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from tutorials import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    # ADMIN paths

    # STUDENT paths

    # TUTOR paths
    # path('api/set-hourly-rate/', views.set_hourly_rate, name='set_hourly_rate'),
    # path('api/set-subjects/', views.set_subjects, name='set_subjects'),
    # path('api/set-availability/', views.set_availability, name='set_availability'),
    path('tutor/availability/', views.TutorAvailabilityView.as_view(), name='tutor_availability'),
    path('tutor/availability/add/', views.AddAvailabilitySlotView.as_view(), name='add_availability_slot'),
    path('tutor/availability/delete/<int:slot_id>/', views.DeleteAvailabilitySlotView.as_view(), name='delete_availability_slot'),
    path('tutor/hourly-rate/', views.TutorHourlyRateView.as_view(), name='tutor_hourly_rate'),
    path('tutor/subjects/', views.TutorSubjectsView.as_view(), name='tutor_subjects'),
    path('tutor/subjects/custom/', views.AddCustomSubjectView.as_view(), name='add_custom_subject'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
