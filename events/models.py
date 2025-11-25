from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Profile for Event Organizers (Companies/Organizations)
class OrganizerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='organizer_profile')
    organization_name = models.CharField(max_length=200)
    organization_type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    logo = models.ImageField(upload_to='organizer_logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.organization_name


# Profile for Volunteers
class VolunteerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='volunteer_profile')
    bio = models.TextField(blank=True)
    interests = models.CharField(max_length=500, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='volunteer_pics/', blank=True, null=True)
    total_events_attended = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Green Events Model
class Event(models.Model):
    CATEGORY_CHOICES = [
        ('tree_planting', '🌳 Tree Planting'),
        ('beach_cleanup', '🏖️ Beach Cleanup'),
        ('recycling', '♻️ Recycling Drive'),
        ('e_waste', '💻 E-Waste Collection'),
        ('community_garden', '🌱 Community Garden'),
        ('workshop', '📚 Sustainability Workshop'),
        ('conservation', '🦋 Nature Conservation'),
        ('cleanup', '🧹 General Cleanup'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    location = models.CharField(max_length=300)
    address = models.TextField(blank=True)
    date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    capacity = models.IntegerField()
    allow_waitlist = models.BooleanField(default=True)
    cover_image = models.ImageField(upload_to='event_covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return self.title

    def spots_remaining(self):
        confirmed = self.registrations.filter(status='confirmed').count()
        return max(0, self.capacity - confirmed)

    def total_registered(self):
        return self.registrations.filter(status='confirmed').count()


# Event Registration
class EventRegistration(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('waitlist', 'Waitlist'),
        ('cancelled', 'Cancelled'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'volunteer']

    def __str__(self):
        return f"{self.volunteer.username} - {self.event.title}"


# User Activity Tracking
class UserHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.user.username} viewed {self.event.title}"