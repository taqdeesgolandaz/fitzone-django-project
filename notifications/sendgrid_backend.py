import sendgrid
from sendgrid.helpers.mail import Mail
from django.conf import settings


class SendGridEmailBackend:
    def send_mail(self, subject, message, from_email, recipient_list, html_message=None, **kwargs):
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
        mail = Mail(
            from_email=from_email,
            to_emails=recipient_list,
            subject=subject,
            html_content=html_message or message,
        )
        response = sg.send(mail)
        return response.status_code == 202
