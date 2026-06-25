import sys
import sendgrid
from sendgrid.helpers.mail import Mail
from django.conf import settings


class SendGridEmailBackend:
    def send_mail(self, subject, message, from_email, recipient_list, html_message=None, **kwargs):
        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        api_key = getattr(settings, 'SENDGRID_API_KEY', '') or getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        if not api_key:
            raise ValueError('SendGrid API key is not configured. Set SENDGRID_API_KEY or EMAIL_HOST_PASSWORD in environment.')

        sg = sendgrid.SendGridAPIClient(api_key)
        mail = Mail(
            from_email=from_email,
            to_emails=recipient_list,
            subject=subject,
            html_content=html_message or message,
            plain_text_content=message,
        )

        response = sg.send(mail)
        if response.status_code != 202:
            print(
                'SendGrid API response:',
                f'Status={response.status_code}',
                f'Body={response.body}',
                f'Headers={response.headers}',
                file=sys.stderr,
            )
        else:
            print(
                'SendGrid email dispatched successfully:',
                f'Status={response.status_code}',
                file=sys.stderr,
            )
        return response.status_code == 202
