from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import send_mail
from notifications.models import EmailLog


class Command(BaseCommand):
    help = 'Test email sending and log results to EmailLog'

    def add_arguments(self, parser):
        parser.add_argument(
            'recipient',
            type=str,
            nargs='?',
            default=None,
            help='Email recipient (optional, defaults to EMAIL_HOST_USER)'
        )

    def handle(self, *args, **options):
        recipient = options.get('recipient') or settings.EMAIL_HOST_USER
        sender = settings.DEFAULT_FROM_EMAIL
        subject = 'FitZone SMTP Test'
        message = 'This is a test email from FitZone to verify SMTP configuration.\n\nIf you received this, email is working correctly!'

        self.stdout.write(f'EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'EMAIL_HOST: {settings.EMAIL_HOST}')
        self.stdout.write(f'EMAIL_PORT: {settings.EMAIL_PORT}')
        self.stdout.write(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
        self.stdout.write(f'DEFAULT_FROM_EMAIL: {sender}')
        self.stdout.write(f'Sending test email to: {recipient}')
        self.stdout.write('')

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=sender,
                recipient_list=[recipient],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('✓ Email sent successfully!'))
            self.stdout.write('Check the inbox (including Spam) for the test email.')
            
            # Also log to EmailLog for record-keeping
            try:
                EmailLog.objects.create(
                    email=recipient,
                    subject=subject,
                    email_type='test',
                    status='sent'
                )
                self.stdout.write('✓ Logged to EmailLog')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Warning: Could not log to EmailLog: {e}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Email send failed: {e}'))
            
            # Log the failure
            try:
                EmailLog.objects.create(
                    email=recipient,
                    subject=subject,
                    email_type='test',
                    status='failed',
                    error_message=str(e)
                )
                self.stdout.write('✓ Failure logged to EmailLog')
            except Exception as log_e:
                self.stdout.write(self.style.WARNING(f'Warning: Could not log failure: {log_e}'))
            
            raise SystemExit(1)
