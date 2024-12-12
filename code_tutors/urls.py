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
    # Common paths
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    
    # Auth paths
    path('dashboard/', views.dashboard, name='dashboard'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('submit_review/', views.submit_review, name='submit_review'),

    # ADMIN paths
    path('dashboard/lesson-request/', views.create_lesson_request, name='lesson_request'),
    path('dashboard/view-lesson-request/', views.view_lesson_request, name='view_lesson_request'),
    path('schedule-session/<int:student_id>/', views.schedule_session, name='schedule_session'),
    path('list/<str:list_type>/', views.user_list, name='user_list'),

    # TUTOR paths
    path('tutor/availability/save', views.tutor_availability, name='tutor_availability'),
    path('tutor/hourly-rate/save', views.tutor_hourly_rate, name='tutor_hourly_rate'),
    path('tutor/subjects/save', views.tutor_subjects, name='tutor_subjects'),
    path('tutor/save-lesson-notes/', views.save_lesson_notes, name='save_lesson_notes'),

    # STUDENT paths
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
