from rest_framework.test import APITestCase
from accounts_app.models import User
from accounts_app.api.serializers import RegisterSerializer, LoginSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from rest_framework.exceptions import AuthenticationFailed

class RegisterSerializerTests(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "Password123!"

    def test_required_fields(self):

        data = {
            "email": self.email,
            "password": self.password,
            "confirmed_password": self.password,
        }
        required_fields = [
            "email",
            "password",
            "confirmed_password",
        ]

        for field in required_fields:
            test_data = data.copy()
            test_data.pop(field)
            serializer = RegisterSerializer(data=test_data)

            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)        

    def test_invalid_password(self):
        serializer = RegisterSerializer(data={
            "email": self.email,
            "new_password": "123",
            "confirm_password": "123",
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_invalid_email(self):
        serializer = RegisterSerializer(data={
            "email": "invalid_mail",
            "password": self.password,
            "confirmed_password": self.password,
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


    def test_passwords_do_not_match(self):
        serializer = RegisterSerializer(data={
            "email": self.email,
            "password": self.password,
            "confirmed_password": "WrongPassword123!",
        })

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            str(serializer.errors["non_field_errors"][0]),
            "Passwords do not match."
        )
        
    def test_duplicate_email(self):
        User.objects.create_user(email=self.email, password=self.password)
        serializer = RegisterSerializer(data={
            "email": self.email,
            "password": self.password,
            "confirmed_password": self.password,
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_serialized_output(self):
        user = User.objects.create_user(email=self.email, password=self.password)
        serializer = RegisterSerializer(user)

        self.assertEqual(serializer.data["email"], self.email)
        self.assertNotIn("password", serializer.data)


class LoginSerializerTests(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "Password123!"
        self.user = User.objects.create_user(email=self.email, password=self.password, is_active=True)
        self.correct_data = {
            "email": self.email,
            "password": self.password,
        }

    def test_success_login(self):
        serializer = LoginSerializer(data=self.correct_data)

        self.assertTrue(serializer.is_valid())

    def test_not_registered_user_login(self):
        serializer = LoginSerializer(data={
            "email": "notRegisteredUser@gmail.com",
            "password": self.password,
        })

        with self.assertRaises(AuthenticationFailed):
            serializer.is_valid(raise_exception=True)

    def test_wrong_password_login(self):
        data = self.correct_data.copy()
        data["password"] = "wrongPassword123!"
        serializer = LoginSerializer(data=data)

        with self.assertRaises(AuthenticationFailed):
            serializer.is_valid(raise_exception=True)

    def test_login_without_password(self):
        data = self.correct_data.copy()
        data.pop("password")
        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_login_without_email(self):
        data = self.correct_data.copy()
        data.pop("email")
        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_inactive_user_login(self):
        email = "seconduser@gmail.com"
        password="strongpassword123!"
        User.objects.create_user(email=email, password=password, is_active=False)
        data = {
            "email": email,
            "password": password,
        }
        serializer = LoginSerializer(data=data)

        with self.assertRaises(AuthenticationFailed):
            serializer.is_valid(raise_exception=True)

    def test_login_without_email_and_password(self):
        serializer = LoginSerializer(data={})

        self.assertFalse(serializer.is_valid())


class PasswordResetRequestSerializerTests(APITestCase):
    def setUp(self):
        self.valid_email = "valid@gmail.com"
        self.user = User.objects.create_user(email=self.valid_email, password="secureTest123!", is_active=True)
        self.valid_data = { "email": self.valid_email }

    def test_valid_email_request(self):
        serializer = PasswordResetRequestSerializer(data=self.valid_data)

        self.assertTrue(serializer.is_valid())

    def test_invalid_email_request(self):
        data = {"email": "invalid-email"}
        serializer = PasswordResetRequestSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_missing_email(self):
        data = {}
        serializer = PasswordResetRequestSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)



class PasswordResetConfirmSerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@gmail.com", password="secureTest123!", is_active=True)        

    def test_valid_passwords(self):
        data = {
            "new_password": "securePassword123!",
            "confirm_password": "securePassword123!",
        }
        serializer = PasswordResetConfirmSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_passwords_do_not_match(self):
        data = {
            "new_password": "securePassword123!",
            "confirm_password": "ANOTHERSecurePassword123!",
        }
        serializer = PasswordResetConfirmSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("confirm_password", serializer.errors)

    def test_invalid_password(self):
        data = {
            "new_password": "invalidpass",
            "confirm_password": "invalidpass",
        }
        serializer = PasswordResetConfirmSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password", serializer.errors)

    def test_missing_new_password(self):
        data = {
            "new_password": "",
            "confirm_password": "securePassword123!",
        }
        serializer = PasswordResetConfirmSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password", serializer.errors)

    def test_missing_confirm_password(self):
        data = {
            "new_password": "securePassword123!",
            "confirm_password": "",
        }
        serializer = PasswordResetConfirmSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("confirm_password", serializer.errors)

