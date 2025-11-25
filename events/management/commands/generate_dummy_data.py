"""
Django Management Command: Generate Dummy Data
Place this file in: events/management/commands/generate_dummy_data.py

Usage: python manage.py generate_dummy_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from events.models import (
    VolunteerProfile, OrganizerProfile, Event, EventRegistration, UserHistory
)


class Command(BaseCommand):
    help = 'Generates dummy data for volunteers, organizers, events, and registrations'

    # Realistic data pools
    FIRST_NAMES = [
        'Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Ethan', 'Sophia', 'Mason',
        'Isabella', 'William', 'Mia', 'James', 'Charlotte', 'Benjamin', 'Amelia',
        'Lucas', 'Harper', 'Henry', 'Evelyn', 'Alexander', 'Abigail', 'Michael',
        'Emily', 'Daniel', 'Elizabeth', 'Matthew', 'Sofia', 'Jackson', 'Avery',
        'Sebastian', 'Ella', 'Jack', 'Scarlett', 'Aiden', 'Grace', 'Owen', 'Chloe',
        'Samuel', 'Victoria', 'David', 'Riley', 'Joseph', 'Aria', 'Carter', 'Lily',
        'Wyatt', 'Aubrey', 'John', 'Zoey', 'Luke', 'Penelope', 'Dylan', 'Lillian',
        'Grayson', 'Addison', 'Isaac', 'Layla', 'Jayden', 'Natalie', 'Levi', 'Camila'
    ]

    LAST_NAMES = [
        'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
        'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
        'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
        'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
        'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
        'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell',
        'Carter', 'Roberts', 'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker'
    ]

    ORGANIZATIONS = [
        'Green Earth Alliance', 'EcoWarriors Foundation', 'Clean Planet Initiative',
        'Sustainable Future Society', 'Ocean Guardians', 'Tree Planters United',
        'Climate Action Network', 'Zero Waste Warriors', 'Renewable Energy Group',
        'Wildlife Conservation Trust', 'Urban Green Spaces', 'Carbon Neutral Coalition',
        'Fresh Air Foundation', 'Solar Power Advocates', 'Recycle Revolution',
        'Green Communities Network', 'Environmental Justice League', 'Nature Lovers Society',
        'Eco Friendly Living', 'Planet Protectors', 'Green Innovation Hub',
        'Sustainable Transport Initiative', 'Clean Water Campaign', 'Earth Day Organizers',
        'Green Tech Solutions', 'Eco Education Foundation', 'Climate Warriors',
        'Green Business Alliance', 'Sustainable Agriculture Network', 'Eco Tourism Group'
    ]

    CITIES = [
        'Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa', 'Edmonton',
        'Mississauga', 'Winnipeg', 'Quebec City', 'Hamilton', 'Brampton',
        'Surrey', 'Kitchener', 'London', 'Victoria', 'Halifax', 'Windsor',
        'Oshawa', 'Saskatoon', 'Regina', 'St. Catharines', 'Kelowna', 'Barrie'
    ]

    EVENT_TITLES = [
        'Community Tree Planting Day', 'Beach Cleanup Drive', 'Renewable Energy Workshop',
        'Zero Waste Lifestyle Seminar', 'Urban Garden Project', 'River Restoration Initiative',
        'Solar Panel Installation Workshop', 'Recycling Education Program', 'Wildlife Conservation Talk',
        'Bike to Work Campaign', 'Composting 101 Workshop', 'Green Building Tour',
        'Climate Change Awareness Rally', 'Organic Farming Workshop', 'Water Conservation Drive',
        'E-Waste Collection Event', 'Nature Trail Cleanup', 'Green Technology Expo',
        'Sustainable Fashion Show', 'Community Garden Opening', 'Environmental Film Screening',
        'Carbon Footprint Workshop', 'Clean Air Initiative', 'Green Energy Fair',
        'Eco-Friendly Products Market', 'Wetlands Restoration Project', 'Bird Watching Event',
        'Green Architecture Seminar', 'Ocean Plastic Cleanup', 'Sustainable Transport Forum'
    ]

    INTERESTS = [
        'Tree Planting', 'Beach Cleaning', 'Recycling', 'Wildlife Conservation',
        'Climate Action', 'Renewable Energy', 'Sustainable Living', 'Urban Gardening',
        'Water Conservation', 'Zero Waste', 'Environmental Education', 'Green Technology'
    ]

    BIOS = [
        'Passionate about making the world a greener place!',
        'Environmental enthusiast committed to sustainable living.',
        'Love nature and want to protect it for future generations.',
        'Dedicated volunteer working towards a cleaner planet.',
        'Believer in the power of community action for environmental change.',
        'Green living advocate and climate action supporter.',
        'Nature lover committed to conservation efforts.',
        'Making a difference one eco-friendly action at a time.',
        'Passionate volunteer for environmental causes.',
        'Sustainability is my lifestyle and my mission.'
    ]

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Starting dummy data generation...'))

        # Clear existing data (optional - comment out if you want to keep existing data)
        self.stdout.write('🗑️  Clearing existing dummy data...')
        User.objects.filter(username__startswith='volunteer_').delete()
        User.objects.filter(username__startswith='organizer_').delete()

        # Generate Volunteers
        self.stdout.write('👥 Creating volunteers...')
        volunteers = self.create_volunteers(100)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(volunteers)} volunteers'))

        # Generate Organizers
        self.stdout.write('🏢 Creating organizers...')
        organizers = self.create_organizers(30)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(organizers)} organizers'))

        # Generate Events
        self.stdout.write('📅 Creating events...')
        events = self.create_events(organizers, 60)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(events)} events'))

        # Generate Registrations
        self.stdout.write('📝 Creating registrations...')
        registrations = self.create_registrations(volunteers, events, 300)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(registrations)} registrations'))

        # Generate User History
        self.stdout.write('📊 Creating user history...')
        history_count = self.create_user_history(volunteers, events)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {history_count} history entries'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('🎉 DUMMY DATA GENERATION COMPLETE!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'👥 Volunteers: {len(volunteers)}')
        self.stdout.write(f'🏢 Organizers: {len(organizers)}')
        self.stdout.write(f'📅 Events: {len(events)}')
        self.stdout.write(f'📝 Registrations: {len(registrations)}')
        self.stdout.write(f'📊 History Entries: {history_count}')
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

    def create_volunteers(self, count):
        """Create volunteer users with profiles"""
        volunteers = []

        for i in range(count):
            first_name = random.choice(self.FIRST_NAMES)
            last_name = random.choice(self.LAST_NAMES)
            username = f'volunteer_{i+1}'
            email = f'{first_name.lower()}.{last_name.lower()}{i}@email.com'

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=first_name,
                last_name=last_name
            )

            # Create volunteer profile
            VolunteerProfile.objects.create(
                user=user,
                bio=random.choice(self.BIOS),
                interests=', '.join(random.sample(self.INTERESTS, random.randint(2, 5))),
                phone=f'+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}',
                city=random.choice(self.CITIES),
                total_events_attended=0  # Will be updated by registrations
            )

            volunteers.append(user)

        return volunteers

    def create_organizers(self, count):
        """Create organizer users with profiles"""
        organizers = []

        for i in range(count):
            first_name = random.choice(self.FIRST_NAMES)
            last_name = random.choice(self.LAST_NAMES)
            username = f'organizer_{i+1}'
            org_name = random.choice(self.ORGANIZATIONS)
            email = f'info@{org_name.lower().replace(" ", "")}{i}.org'

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=first_name,
                last_name=last_name
            )

            # Create organizer profile
            org_types = ['non_profit', 'community_group', 'government', 'educational', 'corporate']
            OrganizerProfile.objects.create(
                user=user,
                organization_name=org_name,
                organization_type=random.choice(org_types),
                description=f'{org_name} is dedicated to environmental conservation and sustainability.',
                website=f'https://www.{org_name.lower().replace(" ", "")}.org',
                phone=f'+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}'
            )

            organizers.append(user)

        return organizers

    def create_events(self, organizers, count):
        """Create events with varied dates (past, present, future)"""
        events = []
        categories = ['cleanup', 'planting', 'education', 'awareness', 'conservation']

        now = timezone.now()

        for i in range(count):
            organizer = random.choice(organizers)

            # Create mix of past, current, and future events
            if i < count // 3:  # Past events
                days_ago = random.randint(1, 180)
                event_date = now - timedelta(days=days_ago)
            elif i < 2 * count // 3:  # Upcoming events (next 90 days)
                days_ahead = random.randint(1, 90)
                event_date = now + timedelta(days=days_ahead)
            else:  # Current/recent events
                days_offset = random.randint(-7, 7)
                event_date = now + timedelta(days=days_offset)

            # Random end date (2-4 hours after start)
            end_date = event_date + timedelta(hours=random.randint(2, 4))

            title = random.choice(self.EVENT_TITLES)
            category = random.choice(categories)
            city = random.choice(self.CITIES)

            event = Event.objects.create(
                organizer=organizer,
                title=f'{title} - {city}',
                description=f'Join us for an amazing {category} event in {city}! This event aims to make a positive impact on our environment and community. All volunteers welcome!',
                category=category,
                location=city,
                address=f'{random.randint(100, 9999)} Green Street, {city}, Canada',
                date=event_date,
                end_date=end_date,
                capacity=random.randint(20, 100),
                allow_waitlist=random.choice([True, False])
            )

            events.append(event)

        return events

    def create_registrations(self, volunteers, events, count):
        """Create event registrations"""
        registrations = []

        # Ensure we don't create duplicate registrations
        registered_pairs = set()

        attempts = 0
        max_attempts = count * 3  # Prevent infinite loop

        while len(registrations) < count and attempts < max_attempts:
            attempts += 1

            volunteer = random.choice(volunteers)
            event = random.choice(events)

            # Check if this pair already exists
            pair = (volunteer.id, event.id)
            if pair in registered_pairs:
                continue

            registered_pairs.add(pair)

            # Determine status based on event capacity
            confirmed_count = EventRegistration.objects.filter(
                event=event,
                status='confirmed'
            ).count()

            if confirmed_count < event.capacity:
                status = 'confirmed'
            else:
                status = 'waitlist' if event.allow_waitlist else 'confirmed'

            # Random registration date (before event date)
            days_before = random.randint(1, 30)
            reg_date = event.date - timedelta(days=days_before)

            registration = EventRegistration.objects.create(
                volunteer=volunteer,
                event=event,
                status=status,
                registered_at=reg_date
            )

            registrations.append(registration)

            # Update volunteer's total events attended (for past events)
            if event.date < timezone.now() and status == 'confirmed':
                profile = volunteer.volunteer_profile
                profile.total_events_attended += 1
                profile.save()

        return registrations

    def create_user_history(self, volunteers, events):
        """Create user browsing history"""
        count = 0

        for volunteer in random.sample(volunteers, min(50, len(volunteers))):
            # Each volunteer views 3-10 random events
            viewed_events = random.sample(events, random.randint(3, 10))

            for event in viewed_events:
                UserHistory.objects.create(
                    user=volunteer,
                    event=event,
                    viewed_at=timezone.now() - timedelta(days=random.randint(0, 30))
                )
                count += 1

        return count