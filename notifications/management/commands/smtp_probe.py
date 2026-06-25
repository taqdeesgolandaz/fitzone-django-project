from django.core.management.base import BaseCommand
from django.conf import settings
import smtplib


def _env_bool(value, default=False):
    if value is None:
        return default
    return str(value).lower() in ['true', '1', 'yes']


class Command(BaseCommand):
    help = 'Probe SMTP server and report supported extensions and auth availability.'

    def handle(self, *args, **options):
        self.stdout.write('SMTP probe starting...')
        self.stdout.write(f'EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'EMAIL_HOST: {settings.EMAIL_HOST}')
        self.stdout.write(f'EMAIL_PORT: {settings.EMAIL_PORT}')
        self.stdout.write(f'EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}')
        self.stdout.write(f'EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'EMAIL_TIMEOUT: {getattr(settings, "EMAIL_TIMEOUT", 30)}')
        self.stdout.write('')

        try:
            if settings.EMAIL_USE_SSL:
                server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=getattr(settings, 'EMAIL_TIMEOUT', 30))
            else:
                server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=getattr(settings, 'EMAIL_TIMEOUT', 30))

            server.set_debuglevel(1)
            server.ehlo()

            if not settings.EMAIL_USE_SSL and settings.EMAIL_USE_TLS:
                self.stdout.write('Starting STARTTLS...')
                server.starttls()
                server.ehlo()

            self.stdout.write('Server extensions:')
            for name, value in server.esmtp_features.items():
                self.stdout.write(f'  {name}: {value}')

            auth_supported = server.has_extn('auth')
            self.stdout.write(f'AUTH supported: {auth_supported}')

            if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
                self.stdout.write('Attempting SMTP login...')
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                self.stdout.write(self.style.SUCCESS('Login succeeded!'))

            server.quit()
            self.stdout.write(self.style.SUCCESS('SMTP probe completed successfully.'))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f'SMTP probe failed: {exc}'))
            raise SystemExit(1)
