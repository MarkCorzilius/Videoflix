from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from accounts_app.models import User
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


class RegisterViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.email = "test@example.com"
        self.password = "Password123!"
        self.register_data = {
            "email": self.email,
            "password": self.password,
            "confirmed_password": self.password,
        }

    def test_register_success(self):
        response = self.client.post("/api/register/", self.register_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_email_returns_400(self):
        User.objects.create_user(email=self.email, password=self.password)
        response = self.client.post("/api/register/", self.register_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email_returns_400(self):
        data = self.register_data.copy()
        data["email"] = "invalid_mail"
        response = self.client.post("/api/register/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weak_password_returns_400(self):
        data = self.register_data.copy()
        data["confirmed_password"] = "123"
        data["password"] = "123"
        response = self.client.post("/api/register/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_passwords_do_not_match_returns_400(self):
        data = self.register_data.copy()
        data["confirmed_password"] = "AnotherPassword123!"
        response = self.client.post("/api/register/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_required_fields_missing(self):
        response = self.client.post("/api/register/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_is_unverified_after_registration(self):
        response = self.client.post("/api/register/", self.register_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=self.email)
        self.assertFalse(user.is_active)

    def test_verification_email_is_sent(self):
        response = self.client.post("/api/register/", self.register_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.email])


class ActivateViewTests(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "Password123!"
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            is_active=False,
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.url = reverse(
            "activate",
            kwargs={
                "uidb64": self.uid,
                "token": self.token,
            },
        )

    def test_activate_user_success(self):
        response = self.client.get(self.url)

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_active)

    def test_activate_user_with_invalid_token(self):
        url = reverse(
            "activate",
            kwargs={
                "uidb64": self.uid,
                "token": "invalid-token",
            },
        )
        response = self.client.get(url)
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.user.is_active)

    def test_activate_user_with_invalid_uid(self):
        url = reverse(
            "activate",
            kwargs={
                "uidb64": "invalid-uid",
                "token": self.token,
            },
        )
        response = self.client.get(url)
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_activate_already_active_user(self):
        self.user.is_active = True
        self.user.save(update_fields=["is_active"])

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)