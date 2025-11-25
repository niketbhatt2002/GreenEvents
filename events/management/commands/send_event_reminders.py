from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from events.models import Event, EventRegistration


class Command(BaseCommand):
    help = 'Send email reminders to volunteers for upcoming events'

    def handle(self, *args, **kwargs):
        now = timezone.now()

        # Get events happening in the next 12 hours
        twelve_hours_from_now = now + timedelta(hours=12)
        events_12h = Event.objects.filter(
            date__gte=now,
            date__lte=twelve_hours_from_now,
            is_active=True
        )

        # Get events happening in the next 1 hour
        one_hour_from_now = now + timedelta(hours=1)
        events_1h = Event.objects.filter(
            date__gte=now,
            date__lte=one_hour_from_now,
            is_active=True
        )

        # Send 12-hour reminders
        for event in events_12h:
            registrations = EventRegistration.objects.filter(
                event=event,
                status='confirmed'
            )

            for registration in registrations:
                try:
                    subject = f'Reminder: {event.title} is in 12 hours!'
                    message = f"""
Hello {registration.volunteer.first_name},

This is a friendly reminder that you're registered for:

Event: {event.title}
Date: {event.date.strftime('%B %d, %Y')}
Time: {event.date.strftime('%I:%M %p')}
Location: {event.location}

Don't forget to bring:
- Comfortable clothes
- Water bottle
- Enthusiasm to make a difference!

See you there!

Best regards,
GreenEvents Team
                    """

                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [registration.volunteer.email],
                        fail_silently=True,
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f'12h reminder sent to {registration.volunteer.email} for {event.title}'
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

        # Send 1-hour reminders
        for event in events_1h:
            registrations = EventRegistration.objects.filter(
                event=event,
                status='confirmed'
            )

            for registration in registrations:
                try:
                    subject = f'STARTING SOON: {event.title} is in 1 hour!'
                    message = f"""
Hello {registration.volunteer.first_name},

🚨 FINAL REMINDER! 🚨

Your event is starting in 1 HOUR!

Event: {event.title}
Time: {event.date.strftime('%I:%M %p')}
Location: {event.location}
Address: {event.address if event.address else 'See event details'}

Get ready and head out soon!

See you there!

Best regards,
GreenEvents Team
                    """

                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [registration.volunteer.email],
                        fail_silently=True,
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f'1h reminder sent to {registration.volunteer.email} for {event.title}'
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Reminder emails sent successfully!'))