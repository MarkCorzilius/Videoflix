import re

from django.core.exceptions import ValidationError


class PasswordStrengthValidator:
    def validate(self, password, user=None):
        """Validate password strength rules and raise ValidationError if any fail."""

        errors = []

        if any(char.isspace() for char in password):
            errors.append("Password must not contain whitespace.")

        if not any(char.islower() for char in password):
            errors.append("Password must contain at least one lowercase letter.")

        if not any(char.isupper() for char in password):
            errors.append("Password must contain at least one uppercase letter.")

        if not any(char.isdigit() for char in password):
            errors.append("Password must contain at least one number.")

        if not any(not char.isalnum() and not char.isspace() for char in password):
            errors.append("Password must contain at least one special character.")

        if re.search(r"(.)\1\1", password):
            errors.append("Password must not contain three or more repeated characters.")

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        """Return a human-readable description of the password requirements."""

        return (
            "Password must contain uppercase and lowercase letters, "
            "a number, and a special character."
        )