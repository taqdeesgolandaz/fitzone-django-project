from django.core.management.base import BaseCommand
from notifications.models import Notification

class Command(BaseCommand):
    help = 'Remove test notifications from the database'

    def handle(self, *args, **options):
        # Delete all notifications with [Test] in the title or message
        deleted_count, _ = Notification.objects.filter(
            title__icontains='[Test]'
        ) | Notification.objects.filter(
            title__icontains='Test Membership'
        ) | Notification.objects.filter(
            message__icontains='[Test]'
        ) | Notification.objects.filter(
            message__icontains='test mode'
        )
        deleted_count = Notification.objects.filter(
            title__icontains='Test'
        ).delete()[0] + Notification.objects.filter(
            message__icontains='test mode'
        ).delete()[0]
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted test notifications')
        )
