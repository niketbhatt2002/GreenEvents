from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added
from .models import VolunteerProfile, OrganizerProfile


@receiver(social_account_added)
def create_profile_on_google_signup(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    account_type = request.session.get('pending_account_type', 'volunteer')

    # Create appropriate profile
    if account_type == 'volunteer':
        if not hasattr(user, 'volunteer_profile'):
            VolunteerProfile.objects.create(user=user)
    elif account_type == 'organizer':
        if not hasattr(user, 'organizer_profile'):
            # Get organization name from Google or use username
            org_name = user.get_full_name() or user.username
            OrganizerProfile.objects.create(user=user, organization_name=org_name)

    # Clear session
    if 'pending_account_type' in request.session:
        del request.session['pending_account_type']