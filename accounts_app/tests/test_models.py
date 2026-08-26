from django.test import TestCase
from accounts_app.models import User
from django.db import IntegrityError


class UserModelTests(TestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "Password123!"
        self.user = User.objects.create_user(email=self.email, password=self.password)

    def test_email_is_unique(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email=self.email, password=self.password)

    def test_password_is_hashed(self):
        self.assertNotEqual(self.user.password, self.password)
        self.assertTrue(self.user.check_password(self.password))