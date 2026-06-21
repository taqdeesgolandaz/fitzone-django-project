from django.core.management.base import BaseCommand
from django.urls import reverse


class Command(BaseCommand):
    help = 'Fix old notification links that point to non-existent admin paths'

    def handle(self, *args, **options):
        from notifications.models import Notification

        mapping = {
            '/admin/notifications/': reverse('notifications:newsletter_subscribers'),
            '/support/admin/messages/': reverse('support:admin_messages'),
            '/admin-dashboard/': reverse('trainers:admin_bookings'),
        }

        total_updated = 0
        for old_link, new_link in mapping.items():
            qs = Notification.objects.filter(link=old_link)
            count = qs.update(link=new_link)
            if count:
                self.stdout.write(self.style.SUCCESS(f'Updated {count} notifications: {old_link} -> {new_link}'))
                total_updated += count

        if total_updated == 0:
            self.stdout.write('No notification links needed updating.')
        else:
            self.stdout.write(self.style.SUCCESS(f'Total notifications updated: {total_updated}'))
