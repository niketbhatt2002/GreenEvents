from django.contrib import admin
from .models import OrganizerProfile, VolunteerProfile, Event, EventRegistration, UserHistory

@admin.register(OrganizerProfile)
class OrganizerProfileAdmin(admin.ModelAdmin):
    list_display = ['organization_name', 'user', 'created_at']

@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'total_events_attended']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'organizer', 'date', 'capacity']
    list_filter = ['category', 'date']

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['event', 'volunteer', 'status', 'registered_at']

@admin.register(UserHistory)
class UserHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'viewed_at']