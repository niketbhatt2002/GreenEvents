from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from allauth.socialaccount.models import SocialAccount
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Event, EventRegistration, VolunteerProfile, OrganizerProfile, UserHistory
from .forms import (
    VolunteerSignupForm, OrganizerSignupForm, EventForm,
    EventSearchForm, ContactForm, VolunteerProfileForm, OrganizerProfileForm
)

import json

# ==================== ANALYTICS HELPER FUNCTIONS ====================

def calculate_volunteer_analytics(user, registrations):
    """Calculate analytics data for volunteer dashboard"""

    # Basic stats
    total_events_registered = registrations.filter(status='confirmed').count()
    upcoming_events = registrations.filter(
        event__date__gte=timezone.now(),
        status='confirmed'
    ).count()
    past_events = registrations.filter(
        event__date__lt=timezone.now(),
        status='confirmed'
    ).count()

    # Environmental Impact Calculations (estimates based on event types)
    trees_planted = past_events * 5  # Assume 5 trees per event on average
    co2_saved = past_events * 25  # 25kg CO2 per event
    waste_collected = past_events * 15  # 15kg waste per event
    hours_volunteered = past_events * 4  # 4 hours per event

    # Achievement Level
    if past_events >= 50:
        achievement_level = "Legend"
        level_progress = 100
    elif past_events >= 25:
        achievement_level = "Expert"
        level_progress = (past_events - 25) / 25 * 100
    elif past_events >= 10:
        achievement_level = "Advanced"
        level_progress = (past_events - 10) / 15 * 100
    elif past_events >= 5:
        achievement_level = "Intermediate"
        level_progress = (past_events - 5) / 5 * 100
    else:
        achievement_level = "Beginner"
        level_progress = past_events / 5 * 100 if past_events > 0 else 0

    # Points system
    total_points = past_events * 10  # 10 points per event

    # Streak calculation (simplified - check if user has recent activity)
    recent_registrations = registrations.filter(
        registered_at__gte=timezone.now() - timedelta(days=30),
        status='confirmed'
    ).order_by('-registered_at')

    if recent_registrations.exists():
        streak_days = (timezone.now() - recent_registrations.first().registered_at).days
        if streak_days > 30:
            streak_days = 0
    else:
        streak_days = 0

    # Activity chart data (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_activity = registrations.filter(
        event__date__gte=six_months_ago,
        event__date__lte=timezone.now(),
        status='confirmed'
    ).annotate(
        month=TruncMonth('event__date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    # Format for chart
    activity_months = []
    activity_counts = []
    for i in range(6):
        month_date = timezone.now() - timedelta(days=30*i)
        activity_months.insert(0, month_date.strftime('%b'))

        # Find count for this month
        count = 0
        for entry in monthly_activity:
            if entry['month'].month == month_date.month and entry['month'].year == month_date.year:
                count = entry['count']
                break
        activity_counts.insert(0, count)

    # Leaderboard (top 10 volunteers by events attended)
    leaderboard = VolunteerProfile.objects.select_related('user').order_by('-total_events_attended')[:10]

    # Add points to leaderboard
    leaderboard_with_points = []
    for profile in leaderboard:
        profile.points = profile.total_events_attended * 10
        leaderboard_with_points.append(profile)

    # Find user's rank
    user_profile = user.volunteer_profile
    leaderboard_rank = VolunteerProfile.objects.filter(
        total_events_attended__gt=user_profile.total_events_attended
    ).count() + 1

    # Percentages for progress bars
    upcoming_percentage = (upcoming_events / max(total_events_registered, 1)) * 100
    completion_percentage = (past_events / max(total_events_registered, 1)) * 100

    return {
        'total_events_registered': total_events_registered,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'trees_planted': trees_planted,
        'co2_saved': co2_saved,
        'waste_collected': waste_collected,
        'hours_volunteered': hours_volunteered,
        'achievement_level': achievement_level,
        'level_progress': int(level_progress),
        'total_points': total_points,
        'streak_days': streak_days,
        'activity_months': json.dumps(activity_months),
        'activity_counts': json.dumps(activity_counts),
        'leaderboard': leaderboard_with_points,
        'leaderboard_rank': leaderboard_rank,
        'upcoming_percentage': int(upcoming_percentage),
        'completion_percentage': int(completion_percentage),
    }


def calculate_organizer_analytics(user, events):
    """Calculate analytics data for organizer dashboard"""

    # Basic counts
    total_events = events.count()
    upcoming_events = events.filter(date__gte=timezone.now()).count()
    past_events = events.filter(date__lt=timezone.now()).count()

    # Percentages
    if total_events > 0:
        upcoming_percentage = (upcoming_events / total_events) * 100
        completion_percentage = (past_events / total_events) * 100
    else:
        upcoming_percentage = 0
        completion_percentage = 0

    # Registration trends (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_registrations = EventRegistration.objects.filter(
        event__organizer=user,
        registered_at__gte=six_months_ago,
        status='confirmed'
    ).annotate(
        month=TruncMonth('registered_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    # Format for chart
    registration_months = []
    registration_counts = []
    for i in range(6):
        month_date = timezone.now() - timedelta(days=30*i)
        registration_months.insert(0, month_date.strftime('%b'))

        # Find count for this month
        count = 0
        for entry in monthly_registrations:
            if entry['month'].month == month_date.month and entry['month'].year == month_date.year:
                count = entry['count']
                break
        registration_counts.insert(0, count)

    # Category distribution
    category_data = events.values('category').annotate(
        count=Count('id')
    ).order_by('-count')

    category_labels = []
    category_counts = []
    for item in category_data:
        # Get display name for category
        category_dict = dict(Event.CATEGORY_CHOICES)
        category_labels.append(category_dict.get(item['category'], item['category']))
        category_counts.append(item['count'])

    return {
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'upcoming_percentage': int(upcoming_percentage),
        'completion_percentage': int(completion_percentage),
        'registration_months': json.dumps(registration_months),
        'registration_counts': json.dumps(registration_counts),
        'category_labels': json.dumps(category_labels),
        'category_counts': json.dumps(category_counts),
        'now': timezone.now(),
    }

# ==================== HOME & PAGES ====================

def home(request):
    """Home page with event listing, search, and pagination"""
    events = Event.objects.all().order_by('-created_at')

    # Search functionality
    search_form = EventSearchForm(request.GET or None)
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        category = search_form.cleaned_data.get('category')

        if query:
            events = events.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query)
            )

        if category:
            events = events.filter(category=category)

    # Add registration count to each event
    events = events.annotate(registration_count=Count('registrations'))

    # ========== ADD PAGINATION ==========
    paginator = Paginator(events, 20)
    page = request.GET.get('page')

    try:
        events_page = paginator.page(page)
    except PageNotAnInteger:
        events_page = paginator.page(1)
    except EmptyPage:
        events_page = paginator.page(paginator.num_pages)
    # ====================================

    # Track visit (sessions & cookies)
    visit_count = request.session.get('visit_count', 0)
    request.session['visit_count'] = visit_count + 1

    context = {
        'events': events_page,  # ← CHANGED from 'events' to 'events_page'
        'search_form': search_form,
        'visit_count': request.session.get('visit_count', 0),
    }
    return render(request, 'events/home.html', context)


def about(request):
    """About page"""
    return render(request, 'pages/about.html')


def contact(request):
    """Contact page with form"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Send email to niketbhatt28@gmail.com
            try:
                send_mail(
                    f'GreenEvents Contact: {subject}',
                    f'From: {name} ({email})\n\n{message}',
                    settings.EMAIL_HOST_USER,  # From address
                    ['niketbhatt28@gmail.com'],  # To address
                    fail_silently=False,
                )
                messages.success(request, 'Thank you! Your message has been sent successfully.')
                return redirect('contact')
            except Exception as e:
                messages.error(request, f'Sorry, there was an error sending your message: {str(e)}')
    else:
        form = ContactForm()

    return render(request, 'pages/contact.html', {'form': form})


# ==================== AUTHENTICATION ====================

def signup_choice(request):
    """Let users choose between Volunteer or Organizer signup"""
    return render(request, 'registration/signup_choice.html')


def volunteer_signup(request):
    """Volunteer signup view"""
    if request.method == 'POST':
        form = VolunteerSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # Get profile picture if uploaded
            profile_picture = form.cleaned_data.get('profile_picture')

            # Create volunteer profile
            VolunteerProfile.objects.create(
                user=user,
                profile_picture=profile_picture
            )

            # Log the user in with explicit backend
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            messages.success(request, f'Welcome {user.first_name}! Your volunteer account has been created! 🎉')
            return redirect('home')
    else:
        form = VolunteerSignupForm()

    return render(request, 'registration/volunteer_signup.html', {'form': form})


def organizer_signup(request):
    """Organizer signup view"""
    if request.method == 'POST':
        form = OrganizerSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # Get form data
            organization_name = form.cleaned_data.get('organization_name')
            logo = form.cleaned_data.get('logo')

            # Create organizer profile
            OrganizerProfile.objects.create(
                user=user,
                organization_name=organization_name,
                logo=logo,
                description=f"Welcome to {organization_name}!"  # Default description
            )

            # Log the user in with explicit backend
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            messages.success(request, f'Welcome {user.first_name}! Your organizer account has been created! 🎉')
            return redirect('home')
    else:
        form = OrganizerSignupForm()

    return render(request, 'registration/organizer_signup.html', {'form': form})


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


# ==================== GOOGLE OAUTH VIEWS ====================

@login_required
def signup_choice_google(request):
    """Show choice page for Google OAuth users"""
    user = request.user

    # If user already has a profile, redirect to home
    if hasattr(user, 'volunteer_profile') or hasattr(user, 'organizer_profile'):
        return redirect('home')

    return render(request, 'account/signup_choice_google.html')


@login_required
def volunteer_google_signup(request):
    """Complete volunteer signup after Google OAuth"""
    user = request.user

    # Check if user already has a profile
    if hasattr(user, 'volunteer_profile') or hasattr(user, 'organizer_profile'):
        messages.info(request, 'You already have a profile!')
        return redirect('my_profile')

    if request.method == 'POST':
        # Get Google account info
        try:
            social_account = SocialAccount.objects.get(user=user, provider='google')
            extra_data = social_account.extra_data

            # Create volunteer profile
            VolunteerProfile.objects.create(
                user=user,
                phone=request.POST.get('phone', ''),
                bio=request.POST.get('bio', 'Joined via Google'),
                interests=request.POST.get('skills', 'Environmental enthusiast')
            )

            messages.success(request, f'Welcome {user.first_name}! Your volunteer account is ready! 🎉')
            return redirect('home')

        except SocialAccount.DoesNotExist:
            messages.error(request, 'Google account not found. Please try again.')
            return redirect('signup_choice')

    return render(request, 'registration/volunteer_google_complete.html')


@login_required
def organizer_google_signup(request):
    """Complete organizer signup after Google OAuth"""
    user = request.user

    # Check if user already has a profile
    if hasattr(user, 'volunteer_profile') or hasattr(user, 'organizer_profile'):
        messages.info(request, 'You already have a profile!')
        return redirect('my_profile')

    if request.method == 'POST':
        # Get Google account info
        try:
            social_account = SocialAccount.objects.get(user=user, provider='google')

            # Create organizer profile
            OrganizerProfile.objects.create(
                user=user,
                organization_name=request.POST.get('organization_name', user.get_full_name()),
                phone=request.POST.get('phone', ''),
                website=request.POST.get('website', ''),
                description=request.POST.get('description', 'Joined via Google')
            )

            messages.success(request, f'Welcome {user.first_name}! Your organizer account is ready! 🎉')
            return redirect('create_event')

        except SocialAccount.DoesNotExist:
            messages.error(request, 'Google account not found. Please try again.')
            return redirect('signup_choice')

    return render(request, 'registration/organizer_google_complete.html')


# ==================== EVENT VIEWS ====================

def event_detail(request, event_id):
    """Event detail view"""
    event = get_object_or_404(Event, pk=event_id)

    # Track recently viewed events (using sessions)
    if request.user.is_authenticated:
        recent_events = request.session.get('recent_events', [])
        if event_id not in recent_events:
            recent_events.insert(0, event_id)
            recent_events = recent_events[:5]  # Keep only last 5
            request.session['recent_events'] = recent_events

        # Create user history
        UserHistory.objects.create(
            user=request.user,
            event=event
        )

    # Check if user is registered
    is_registered = False
    user_registration = None
    if request.user.is_authenticated:
        user_registration = EventRegistration.objects.filter(
            volunteer=request.user,
            event=event,
            status__in=['confirmed', 'waitlist']
        ).first()
        is_registered = user_registration is not None

    # Get registration count
    registration_count = event.registrations.filter(status='confirmed').count()
    available_spots = event.capacity - registration_count

    context = {
        'event': event,
        'is_registered': is_registered,
        'user_registration': user_registration,
        'registration_count': registration_count,
        'available_spots': available_spots,
    }
    return render(request, 'events/event_detail.html', context)


@login_required
def create_event(request):
    """Create new event (organizers only)"""
    # Check if user is an organizer
    if not hasattr(request.user, 'organizer_profile'):
        messages.error(request, 'Only organizers can create events.')
        return redirect('home')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()

            messages.success(request, f'Event "{event.title}" created successfully! 🎉')
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm()

    return render(request, 'events/create_event.html', {'form': form})


@login_required
def edit_event(request, event_id):
    """Edit event (organizer only)"""
    event = get_object_or_404(Event, pk=event_id)

    # Check if user is the organizer
    if event.organizer != request.user:
        messages.error(request, 'You can only edit your own events.')
        return redirect('event_detail', event_id=event.id)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f'Event "{event.title}" updated successfully!')
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)

    return render(request, 'events/edit_event.html', {'form': form, 'event': event})


@login_required
def delete_event(request, event_id):
    """Delete event (organizer only)"""
    event = get_object_or_404(Event, pk=event_id)

    # Check if user is the organizer
    if event.organizer != request.user:
        messages.error(request, 'You can only delete your own events.')
        return redirect('event_detail', event_id=event.id)

    if request.method == 'POST':
        event_title = event.title
        event.delete()
        messages.success(request, f'Event "{event_title}" deleted successfully.')
        return redirect('home')

    return render(request, 'events/delete_event.html', {'event': event})


# ==================== REGISTRATION VIEWS ====================

@login_required
def register_for_event(request, event_id):
    """Register for an event (volunteers only)"""
    event = get_object_or_404(Event, pk=event_id)

    # Check if user is a volunteer
    if not hasattr(request.user, 'volunteer_profile'):
        messages.error(request, 'Only volunteers can register for events.')
        return redirect('event_detail', event_id=event.id)

    # Check if already registered (including cancelled - allow re-registration if cancelled)
    existing_registration = EventRegistration.objects.filter(
        volunteer=request.user,
        event=event
    ).first()

    if existing_registration:
        if existing_registration.status in ['confirmed', 'waitlist']:
            messages.warning(request, 'You are already registered for this event.')
            return redirect('event_detail', event_id=event.id)
        elif existing_registration.status == 'cancelled':
            # Allow re-registration - update existing registration
            confirmed_count = event.registrations.filter(status='confirmed').count()

            if confirmed_count < event.capacity:
                existing_registration.status = 'confirmed'
                message_text = f'Successfully re-registered for "{event.title}"! 🎉'
            else:
                existing_registration.status = 'waitlist'
                message_text = f'You have been added to the waitlist for "{event.title}".'

            existing_registration.registered_at = timezone.now()
            existing_registration.save()

            messages.success(request, message_text)
            return redirect('event_detail', event_id=event.id)

    # Check capacity for new registration
    confirmed_count = event.registrations.filter(status='confirmed').count()

    if confirmed_count < event.capacity:
        status = 'confirmed'
        message_text = f'Successfully registered for "{event.title}"! 🎉'
    else:
        status = 'waitlist'
        message_text = f'You have been added to the waitlist for "{event.title}".'

    # Create registration
    registration = EventRegistration.objects.create(
        volunteer=request.user,
        event=event,
        status=status
    )

    # Create user history
    UserHistory.objects.create(
        user=request.user,
        event=event
    )

    # Send confirmation email to volunteer (acts as ticket)
    try:
        email_subject = f'🎟️ Your Event Ticket - {event.title}'
        email_body = f'''
Dear {request.user.first_name or request.user.username},

🎉 Congratulations! Your registration has been confirmed.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 EVENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌱 Event: {event.title}
📅 Date: {event.date.strftime("%B %d, %Y")}
⏰ Time: {event.date.strftime("%I:%M %p")}
📍 Location: {event.location}
👥 Category: {event.get_category_display()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ REGISTRATION STATUS: {status.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📧 Volunteer: {request.user.get_full_name() or request.user.username}
📬 Email: {request.user.email}
🆔 Registration ID: {EventRegistration.objects.filter(volunteer=request.user, event=event).first().id if EventRegistration.objects.filter(volunteer=request.user, event=event).exists() else 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💚 Thank you for being part of the green movement!

Please save this email as your event ticket. Show this confirmation at the event.

Need to cancel? Log in to your GreenEvents profile to manage your registrations.

Best regards,
The GreenEvents Team
🌍 Making the world greener, one event at a time!
        '''

        send_mail(
            email_subject,
            email_body,
            settings.EMAIL_HOST_USER,
            [request.user.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error sending volunteer email: {e}")

    # Send notification email to organizer
    try:
        organizer_email = event.organizer.email
        email_subject = f'📝 New Registration for {event.title}'
        email_body = f'''
Dear {event.organizer.first_name or event.organizer.username},

Great news! A new volunteer has registered for your event.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 EVENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌱 Event: {event.title}
📅 Date: {event.date.strftime("%B %d, %Y at %I:%M %p")}
📍 Location: {event.location}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 VOLUNTEER DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Name: {request.user.get_full_name() or request.user.username}
Email: {request.user.email}
Status: {status.upper()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 CURRENT REGISTRATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Confirmed: {EventRegistration.objects.filter(event=event, status='confirmed').count()}
Capacity: {event.capacity}
Remaining Spots: {event.capacity - EventRegistration.objects.filter(event=event, status='confirmed').count()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You can view all registrations and manage your event in your organizer dashboard.

Best regards,
The GreenEvents Team
🌍 Supporting your green initiatives!
        '''

        send_mail(
            email_subject,
            email_body,
            settings.EMAIL_HOST_USER,
            [organizer_email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error sending organizer email: {e}")

    messages.success(request, message_text)
    return redirect('event_detail', event_id=event.id)


@login_required
def cancel_registration(request, event_id):
    """Cancel registration for an event"""
    event = get_object_or_404(Event, pk=event_id)

    registration = get_object_or_404(
        EventRegistration,
        volunteer=request.user,
        event=event,
        status__in=['confirmed', 'waitlist']
    )

    # Cancel the registration
    registration.status = 'cancelled'
    registration.save()

    # Create user history
    UserHistory.objects.create(
        user=request.user,
        event=event
    )

    messages.success(request, f'Registration cancelled for "{event.title}". You can re-register anytime!')
    return redirect('my_profile')


@login_required
def view_registrations(request, event_id):
    """View all registrations for an event (organizer only)"""
    event = get_object_or_404(Event, pk=event_id)

    # Check if user is the organizer
    if event.organizer != request.user:
        messages.error(request, 'You can only view registrations for your own events.')
        return redirect('event_detail', event_id=event.id)

    registrations = event.registrations.all().order_by('-registered_at')
    confirmed = registrations.filter(status='confirmed')
    waitlist = registrations.filter(status='waitlist')

    context = {
        'event': event,
        'registrations': registrations,
        'confirmed': confirmed,
        'waitlist': waitlist,
    }
    return render(request, 'events/view_registrations.html', context)


# ==================== PROFILE VIEWS ====================
@login_required
def my_profile(request):
    """Unified profile page for both volunteers and organizers with analytics"""
    user = request.user

    # Check user type
    is_volunteer = hasattr(user, 'volunteer_profile')
    is_organizer = hasattr(user, 'organizer_profile')

    if is_volunteer:
        profile = user.volunteer_profile

        # Get user's registrations
        registrations = EventRegistration.objects.filter(
            volunteer=user,
            status__in=['confirmed', 'waitlist']
        ).select_related('event').order_by('-registered_at')

        # Get recently viewed events
        recent_event_ids = request.session.get('recent_events', [])
        recent_events = Event.objects.filter(id__in=recent_event_ids)

        # Calculate analytics
        analytics = calculate_volunteer_analytics(user, registrations)

        # Update profile's total events attended
        profile.total_events_attended = analytics['past_events']
        profile.save()

        context = {
            'profile': profile,
            'is_volunteer': True,
            'registrations': registrations,
            'recent_events': recent_events,
            **analytics  # Unpack all analytics data
        }
        return render(request, 'events/volunteer_dashboard.html', context)

    elif is_organizer:
        profile = user.organizer_profile

        # Get organizer's events
        events = Event.objects.filter(organizer=user).annotate(
            registration_count=Count('registrations', filter=Q(registrations__status='confirmed'))
        ).order_by('-created_at')

        # Get total registrations across all events
        total_registrations = EventRegistration.objects.filter(
            event__organizer=user,
            status='confirmed'
        ).count()

        # Calculate analytics
        analytics = calculate_organizer_analytics(user, events)

        context = {
            'profile': profile,
            'is_organizer': True,
            'events': events,
            'total_registrations': total_registrations,
            **analytics  # Unpack all analytics data
        }
        return render(request, 'events/organizer_dashboard.html', context)

    else:
        messages.error(request, 'Profile not found. Please complete your signup.')
        return redirect('signup_choice')


@login_required
def edit_volunteer_profile(request):
    """Edit volunteer profile"""
    if not hasattr(request.user, 'volunteer_profile'):
        messages.error(request, 'You do not have a volunteer profile.')
        return redirect('home')

    profile = request.user.volunteer_profile

    if request.method == 'POST':
        form = VolunteerProfileForm(request.POST, request.FILES, instance=profile)  # ← ADDED request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('my_profile')
    else:
        form = VolunteerProfileForm(instance=profile)

    return render(request, 'events/edit_volunteer_profile.html', {'form': form})

@login_required
def edit_organizer_profile(request):
    """Edit organizer profile"""
    if not hasattr(request.user, 'organizer_profile'):
        messages.error(request, 'You do not have an organizer profile.')
        return redirect('home')

    profile = request.user.organizer_profile

    if request.method == 'POST':
        form = OrganizerProfileForm(request.POST, request.FILES, instance=profile)  # ← ADDED request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('my_profile')
    else:
        form = OrganizerProfileForm(instance=profile)

    return render(request, 'events/edit_organizer_profile.html', {'form': form})