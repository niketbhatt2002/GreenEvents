from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to handle Google OAuth signup/login flow intelligently.
    - If user exists with same email, links Google account to existing user
    - If new user, redirects to profile type selection page
    - If existing Google user, goes straight to home
    """

    def pre_social_login(self, request, sociallogin):
        """
        Check if a user with this email already exists and link accounts.
        This allows existing users to login with Google without creating duplicates.
        """
        # If this social account is already connected, do nothing
        if sociallogin.is_existing:
            return

        # If user is already logged in, do nothing (linking accounts)
        if request.user.is_authenticated:
            return

        # Get email from Google
        email = sociallogin.account.extra_data.get('email')
        if not email:
            return

        # Check if a user with this email already exists
        try:
            existing_user = User.objects.get(email=email)

            # Link the Google account to the existing user
            sociallogin.connect(request, existing_user)

            # Log them in as the existing user
            # The login will happen automatically after this method

        except User.DoesNotExist:
            # No existing user, will create new one
            pass
        except User.MultipleObjectsReturned:
            # Multiple users with same email - use the first one
            existing_user = User.objects.filter(email=email).first()
            sociallogin.connect(request, existing_user)

    def get_login_redirect_url(self, request):
        """
        Returns the URL to redirect to after successful login.
        - If user has profile → go to home
        - If new Google user → go to choice page
        """
        user = request.user

        # Check if user has any profile
        has_volunteer_profile = hasattr(user, 'volunteer_profile')
        has_organizer_profile = hasattr(user, 'organizer_profile')

        if has_volunteer_profile or has_organizer_profile:
            # User has a profile, go to home
            return '/'

        # New Google user without profile - send to choice page ONE TIME
        return '/signup-choice-google/'

    def save_user(self, request, sociallogin, form=None):
        """
        Saves a new user instance using information from the social login.
        Extracts name from Google data.
        """
        user = super().save_user(request, sociallogin, form)

        # Extract additional data from Google
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data

            # Update user with Google data if not already set
            if not user.first_name and 'given_name' in extra_data:
                user.first_name = extra_data.get('given_name', '')

            if not user.last_name and 'family_name' in extra_data:
                user.last_name = extra_data.get('family_name', '')

            # Ensure email is set
            if not user.email and 'email' in extra_data:
                user.email = extra_data.get('email', '')

            user.save()

        return user

    def populate_user(self, request, sociallogin, data):
        """
        Populate user information from social login data.
        """
        user = super().populate_user(request, sociallogin, data)

        # Ensure email is always set from Google
        if not user.email and 'email' in sociallogin.account.extra_data:
            user.email = sociallogin.account.extra_data.get('email')

        return user