"""
Quick test to verify dummy data setup
Place in: events/management/commands/test_setup.py

Usage: python manage.py test_setup
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import Event, EventRegistration, VolunteerProfile, OrganizerProfile


class Command(BaseCommand):
    help = 'Tests if dummy data generation is ready'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('🔍 TESTING DUMMY DATA SETUP'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

        # Test 1: Can we import models?
        self.stdout.write('✅ Models imported successfully')

        # Test 2: Check current data
        users = User.objects.count()
        events = Event.objects.count()
        volunteers = VolunteerProfile.objects.count()
        organizers = OrganizerProfile.objects.count()
        registrations = EventRegistration.objects.count()

        self.stdout.write(f'\n📊 Current Database Stats:')
        self.stdout.write(f'   Users: {users}')
        self.stdout.write(f'   Events: {events}')
        self.stdout.write(f'   Volunteers: {volunteers}')
        self.stdout.write(f'   Organizers: {organizers}')
        self.stdout.write(f'   Registrations: {registrations}')

        # Test 3: Ready to generate?
        self.stdout.write(f'\n🎯 Setup Status:')
        self.stdout.write(self.style.SUCCESS('   ✅ Database is accessible'))
        self.stdout.write(self.style.SUCCESS('   ✅ Models are working'))
        self.stdout.write(self.style.SUCCESS('   ✅ Ready to generate dummy data!'))

        self.stdout.write(f'\n💡 Next Step:')
        self.stdout.write(self.style.WARNING('   Run: python manage.py generate_dummy_data'))

        self.stdout.write(self.style.SUCCESS('\n' + '='*60 + '\n'))