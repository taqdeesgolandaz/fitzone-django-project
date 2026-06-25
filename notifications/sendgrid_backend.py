import sys

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
from django.core.mail.message import EmailMessage


try:
    import sendgrid
    from sendgrid.helpers.mail import Mail
except ImportError:
    sendgrid = None
    Mail = None


class SendGridEmailBackend(BaseEmailBackend):
    """Custom Django email backend using the SendGrid API."""

    def _get_api_key(self):
        return getattr(settings, 'SENDGRID_API_KEY', '') or getattr(settings, 'EMAIL_HOST_PASSWORD', '')

    def _build_mail(self, message: EmailMessage):
        html_content = None
        if hasattr(message, 'alternatives') and message.alternatives:
            html_content = message.alternatives[0][0]
        elif message.content_subtype == 'html':
            html_content = message.body

        return Mail(
            from_email=message.from_email or settings.DEFAULT_FROM_EMAIL,
            to_emails=list(message.to) if message.to else [],
            subject=message.subject,
            html_content=html_content or message.body,
            plain_text_content=message.body if html_content else message.body,
        )

    def _smtp_fallback(self):
        return SMTPEmailBackend(
            host=getattr(settings, 'EMAIL_HOST', ''),
            port=getattr(settings, 'EMAIL_PORT', ''),
            username=getattr(settings, 'EMAIL_HOST_USER', ''),
            password=getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
            use_tls=getattr(settings, 'EMAIL_USE_TLS', False),
            use_ssl=getattr(settings, 'EMAIL_USE_SSL', False),
            fail_silently=self.fail_silently,
            timeout=getattr(settings, 'EMAIL_TIMEOUT', None),
        )

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        api_key = self._get_api_key()
        if not sendgrid or not Mail:
            if self._can_use_smtp_fallback():
                print('SendGrid package unavailable; falling back to SMTP email backend.', file=sys.stderr)
                return self._smtp_fallback().send_messages(email_messages)
            raise ImportError('SendGrid package is not installed. Install sendgrid or configure a SMTP backend.')

        if not api_key:
            if self._can_use_smtp_fallback():
                print('SendGrid API key missing; falling back to SMTP email backend.', file=sys.stderr)
                return self._smtp_fallback().send_messages(email_messages)
            raise ValueError('SendGrid API key is not configured. Set SENDGRID_API_KEY or EMAIL_HOST_PASSWORD in environment.')

        sg = sendgrid.SendGridAPIClient(api_key)
        sent_count = 0

        for message in email_messages:
            if not isinstance(message, EmailMessage):
                continue

            mail = self._build_mail(message)
            try:
                response = sg.send(mail)
            except Exception as e:
                if self._can_use_smtp_fallback():
                    print('SendGrid API send failed; retrying via SMTP backend.', file=sys.stderr)
                    return self._smtp_fallback().send_messages(email_messages)
                if not self.fail_silently:
                    raise
                print(f'SendGrid send failed: {e}', file=sys.stderr)
                continue

            if response.status_code == 202:
                sent_count += 1
                print(
                    'SendGrid email dispatched successfully:',
                    f'Status={response.status_code}',
                    file=sys.stderr,
                )
            else:
                print(
                    'SendGrid API response:',
                    f'Status={response.status_code}',
                    f'Body={response.body}',
                    f'Headers={response.headers}',
                    file=sys.stderr,
                )
        return sent_count

    def _can_use_smtp_fallback(self):
        host = getattr(settings, 'EMAIL_HOST', '')
        port = getattr(settings, 'EMAIL_PORT', '')
        return bool(host and port)
