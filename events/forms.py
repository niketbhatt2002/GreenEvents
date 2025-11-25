from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Event, OrganizerProfile, VolunteerProfile


# VOLUNTEER SIGNUP FORM
class VolunteerSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    profile_picture = forms.ImageField(required=False, help_text="Upload your profile picture (optional)")
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


# ORGANIZER SIGNUP FORM
class OrganizerSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    organization_name = forms.CharField(max_length=200, required=True)
    logo = forms.ImageField(required=False, help_text="Upload your organization logo (optional)")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'organization_name']


# VOLUNTEER PROFILE FORM
class VolunteerProfileForm(forms.ModelForm):
    class Meta:
        model = VolunteerProfile
        fields = ['bio', 'interests', 'phone', 'city', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }


# ORGANIZER PROFILE FORM
class OrganizerProfileForm(forms.ModelForm):
    class Meta:
        model = OrganizerProfile
        fields = ['organization_name', 'organization_type', 'description', 'website', 'phone', 'logo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


# EVENT CREATE/EDIT FORM
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'location', 'address',
                  'date', 'end_date', 'capacity', 'allow_waitlist', 'cover_image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


# SEARCH FORM
class EventSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search events...'})
    )
    category = forms.ChoiceField(
        required=False,
        choices=[('', 'All Categories')] + Event.CATEGORY_CHOICES
    )


# CONTACT FORM
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))