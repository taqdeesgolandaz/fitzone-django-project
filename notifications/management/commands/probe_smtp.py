from django.core.management.base import BaseCommand
from django.conf import settings
import smtplib


class Command(BaseCommand):
    help = 'Probe SMTP server (EHLO and AUTH ext) using configured EMAIL_* settings'

    def handle(self, *args, **options):
        host = getattr(settings, 'EMAIL_HOST', 'localhost')
        port = getattr(settings, 'EMAIL_PORT', 25)
        use_tls = getattr(settings, 'EMAIL_USE_TLS', False)
        use_ssl = getattr(settings, 'EMAIL_USE_SSL', False)
        timeout = getattr(settings, 'EMAIL_TIMEOUT', 10)

        self.stdout.write(f'Probing SMTP {host}:{port} (tls={use_tls} ssl={use_ssl})')

        try:
            if use_ssl:
                server = smtplib.SMTP_SSL(host, port, timeout=timeout)
            else:
                server = smtplib.SMTP(host, port, timeout=timeout)

            server.set_debuglevel(1)
            ehlo_res = server.ehlo()
            self.stdout.write(f'EHLO response: {ehlo_res}')

            if use_tls:
                starttls_res = server.starttls()
                self.stdout.write(f'STARTTLS response: {starttls_res}')
                server.ehlo()

            auth_supported = server.has_extn('auth')
            self.stdout.write(f'AUTH supported?: {auth_supported}')

            try:
                server.quit()
            except Exception:
                pass

        except Exception as e:
            self.stderr.write(f'Error probing SMTP: {e}')