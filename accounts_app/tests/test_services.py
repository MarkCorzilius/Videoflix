from django.test import TestCase
from accounts_app.models import User
from django.core import mail
from accounts_app.tasks.email_tasks import send_verification_email_task, send_password_reset_task
from django.contrib.auth.tokens import default_token_generator

class EmailServiceTests(TestCase):

    def setUp(self):
        self.email = "test@example.com"
        self.password = "Password123!"

        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
        )

    def test_verification_email_is_sent(self):
        token = default_token_generator.make_token(self.user)
        send_verification_email_task(self.user.id, token)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.email])


class PasswordResetRequestServiceTests(TestCase):

    def setUp(self):
        self.email = "valid@gmail.com"
        self.user = User.objects.create_user(email=self.email, password="secureTest123!", is_active=True)

    def test_password_reset_request_sends_email(self):
        token = default_token_generator.make_token(self.user)
        send_password_reset_task(self.user.id, token)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.email])

        
