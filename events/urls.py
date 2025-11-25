from django.urls import path
from . import views

urlpatterns = [
    # Home (Class-Based View)
    path('', views.home, name='home'),

    # Authentication
    path('signup/', views.signup_choice, name='signup_choice'),
    path('signup/volunteer/', views.volunteer_signup, name='volunteer_signup'),
    path('signup/organizer/', views.organizer_signup, name='organizer_signup'),
    path('logout/', views.logout_view, name='logout'),

    # Events
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/create/', views.create_event, name='create_event'),
    path('event/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('event/<int:event_id>/delete/', views.delete_event, name='delete_event'),

    # Registration
    path('event/<int:event_id>/register/', views.register_for_event, name='register_event'),
    path('event/<int:event_id>/cancel/', views.cancel_registration, name='cancel_registration'),
    path('event/<int:event_id>/registrations/', views.view_registrations, name='view_registrations'),

    # Dashboards
    path('my-profile/', views.my_profile, name='my_profile'),
    path('volunteer/edit-profile/', views.edit_volunteer_profile, name='edit_volunteer_profile'),
    path('organizer/edit-profile/', views.edit_organizer_profile, name='edit_organizer_profile'),

    # Pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

# Google OAuth Signup
    path('signup-choice-google/', views.signup_choice_google, name='signup_choice_google'),
    path('signup/volunteer/google/', views.volunteer_google_signup, name='volunteer_google_signup'),
    path('signup/organizer/google/', views.organizer_google_signup, name='organizer_google_signup'),
]