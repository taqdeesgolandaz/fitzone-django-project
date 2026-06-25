from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()


class ForgotPasswordTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='secret123',
        )

    def test_forgot_password_redirects_when_email_sent(self):
        with patch('accounts.views.send_mail') as mock_send_mail:
            mock_send_mail.return_value = 1
            response = self.client.post(
                reverse('forgot_password'),
                {'email': self.user.email},
                HTTP_HOST='localhost'
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        self.assertTrue(mock_send_mail.called)

    def test_forgot_password_shows_error_on_email_failure(self):
        with patch('accounts.views.send_mail', side_effect=Exception('send failed')) as mock_send_mail:
            response = self.client.post(
                reverse('forgot_password'),
                {'email': self.user.email},
                HTTP_HOST='localhost'
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unable to send password reset email right now.')
        self.assertTrue(mock_send_mail.called)
