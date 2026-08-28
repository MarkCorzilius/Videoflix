from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from accounts_app.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.core.cache import cache
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken


class RegisterViewTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

        self.email = "test@example.com"
        self.password = "Password123!"
        self.register_data = {
            "email": self.email,
            "password": self.password,
            "confirmed_password": self.password,
        }
        self.url = "/api/register/"

    def test_register_success(self):
        response = self.client.post(self.url, self.register_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_throttle(self):
        last_user_data = {
                "email": f"lastuser@example.com",
                "password": "Password123!",
                "confirmed_password": "Password123!",
            }
        for i in range(10):
            data = {
                "email": f"user{i}@example.com",
                "password": "Password123!",
                "confirmed_password": "Password123!",
            }
            response = self.client.post(self.url, data, format="json", REMOTE_ADDR="192.168.1.1")
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        response = self.client.post(self.url, last_user_data, format="json", REMOTE_ADDR="192.168.1.1")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_different_ips_have_different_throttle_rates(self):
        last_user_data = {
                "email": f"lastuser@example.com",
                "password": "Password123!",
                "confirmed_password": "Password123!",
            }
        for i in range(10):
            data = {
                "email": f"user{i}@example.com",
                "password": "Password123!",
                "confirmed_password": "Password123!",
            }
            response = self.client.post(self.url, data, format="json", REMOTE_ADDR="192.168.1.1")
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        response = self.client.post(self.url, data, format="json", REMOTE_ADDR="192.168.1.1")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        response = self.client.post(self.url, last_user_data, format="json", REMOTE_ADDR="192.168.1.2")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_email_returns_400(self):
        User.objects.create_user(email=self.email, password=self.password)
        response = self.client.post(self.url, self.register_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email_returns_400(self):
        data = self.register_data.copy()
        data["email"] = "invalid_mail"
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weak_password_returns_400(self):
        data = self.register_data.copy()
        data["confirmed_password"] = "123"
        data["password"] = "123"
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_passwords_do_not_match_returns_400(self):
        data = self.register_data.copy()
        data["confirmed_password"] = "AnotherPassword123!"
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_required_fields_missing(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_is_unverified_after_registration(self):
        response = self.client.post(self.url, self.register_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=self.email)
        self.assertFalse(user.is_active)


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


class LoginViewTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.email = "test@example.com"
        self.password = "Password123!"
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            is_active=True,
        )
        self.client = APIClient()

        self.correct_data = {
            "email": self.email,
            "password": self.password
        }

        self.expected_response = {
            "detail": "Login successful",
                "user": {
                    "id": self.user.id,
                    "username": self.user.username,
                }
        }
        self.url = "/api/login/"

    def test_success_login(self):
        response = self.client.post(self.url, data=self.correct_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_throttle(self):
        for _ in range(10):
            response = self.client.post(self.url, self.correct_data, format="json")
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        response = self.client.post(self.url, self.correct_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_different_emails_have_different_throttle_rates(self):
        for _ in range(10):
            response = self.client.post(self.url, self.correct_data, format="json")
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        response = self.client.post(self.url, self.correct_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        User.objects.create_user(email="foreign@mail.com", password="securePassword123!", is_active=True)
        response = self.client.post(self.url, data={
            "email": "foreign@mail.com",
            "password": "securePassword123!",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_correct_response(self):
        response = self.client.post(self.url, data=self.correct_data, format="json")

        self.assertEqual(response.data, self.expected_response)

    def test_success_login_created_cookies(self):
        response = self.client.post(self.url, data=self.correct_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.cookies)
        self.assertIn("refresh", response.cookies)

    def test_login_wrong_email(self):
        data = self.correct_data.copy()
        data["email"] = "wrongmail@mail.com"
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_wrong_password(self):
        data = self.correct_data.copy()
        data["password"] = "wrongpass"
        response = self.client.post(self.url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_login_missing_fields(self):
        for field in self.correct_data:
            data = self.correct_data.copy()
            data.pop(field)
            response = self.client.post(self.url, data=data, format="json")

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_empty_request(self):
        response = self.client.post(self.url, data={}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unverified_login(self):
        email="supertest@gmail.com"
        password="strongPass123!"
        User.objects.create_user(email=email, password=password, is_active=False)
        response = self.client.post(self.url, data={
            "email": email,
            "password": password,
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RefreshTokenViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = "supertest@gmail.com"
        self.password = "strongPass123!"
        self.user = User.objects.create_user(email=self.email, password=self.password, is_active=True)

    def test_fresh_refresh_token_creates_access_token(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies["refresh"] = str(refresh)
        response = self.client.post("/api/token/refresh/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_expired_refresh_token_denies_access(self):
        refresh = RefreshToken.for_user(self.user)
        refresh.set_exp(lifetime=timedelta(seconds=-1))
        self.client.cookies["refresh"] = str(refresh)
        response = self.client.post("/api/token/refresh/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_refresh_token_denies_access(self):
        response = self.client.post("/api/token/refresh/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_refresh_token_denies_access(self):
        self.client.cookies["refresh"] = str("invalid_refresh_token")
        response = self.client.post("/api/token/refresh/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_blacklisted_refresh_token_denies_access(self):
        refresh = RefreshToken.for_user(self.user)
        refresh.blacklist()
        self.client.cookies["refresh"] = str(refresh)
        response = self.client.post("/api/token/refresh/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutViewTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(email="test@gmail.com", password="securetest123!", is_active=True)
        self.refresh = RefreshToken.for_user(self.user)
        self.client.cookies["refresh"] = str(self.refresh)

        self.logout_url = "/api/logout/"

    def test_successful_logout(self):
        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.cookies["refresh"]["max-age"], 0)
        self.assertEqual(response.cookies["access"]["max-age"], 0)

    def test_verify_refresh_token_is_blacklisted(self):
        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(BlacklistedToken.objects.filter(token__jti=self.refresh["jti"]).exists())


    def test_logout_without_refresh_token_cookie(self):
        self.client.cookies["refresh"] = ""
        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(BlacklistedToken.objects.filter(token__jti=self.refresh["jti"]).exists())
        
        self.assertEqual(response.cookies["refresh"]["max-age"], 0)
        self.assertEqual(response.cookies["access"]["max-age"], 0)

    def test_logout_with_invalid_token(self):
        self.client.cookies["refresh"] = str("invalid-token")
        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(BlacklistedToken.objects.filter(token__jti=self.refresh["jti"]).exists())
        
        self.assertEqual(response.cookies["refresh"]["max-age"], 0)
        self.assertEqual(response.cookies["access"]["max-age"], 0)