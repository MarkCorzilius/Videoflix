from django_rq import job

from accounts_app.models import User
from accounts_app.services.email_services import send_password_reset_service, send_verification_email


@job("default")
def send_verification_email_task(user_id, token):
    """Background job that sends the account verification email to a user."""

    user = User.objects.get(pk=user_id)
    send_verification_email(user, token)


@job("default")
def send_password_reset_task(user_id, token):
    """Background job that sends the password reset email to a user."""

    user = User.objects.get(pk=user_id)
    send_password_reset_service(user, token)
