from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_verification_email(user, token):
    """Send an account activation email containing the verification link."""

    uid = urlsafe_base64_encode(force_bytes(user.id))
    activation_link = f"/api/activate/{uid}/{token}/"

    text_content = render_to_string("accounts/emails/verification_email.txt", {
        "user": user,
        "activation_link": activation_link,
        }
    )

    html_content = render_to_string("accounts/emails/verification_email.html", {
        "user": user,
        "activation_link": activation_link,
        }
    )

    msg = EmailMultiAlternatives(
        subject="Confirm you email",
        body=text_content,
        from_email="Videoflix@mail.com",
        to=[user.email],
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_password_reset_service(user, token):
    """Send a password reset email containing the reset link."""

    uidb64 = urlsafe_base64_encode(force_bytes(user.id))
    reset_url = f"/api/password_confirm/{uidb64}/{token}/"

    text_content = render_to_string(
        "accounts/emails/password_reset.txt",
        context={"reset_url": reset_url},
    )

    html_content = render_to_string(
        "accounts/emails/password_reset.html",
        context={"reset_url": reset_url},
    )

    msg = EmailMultiAlternatives(
        subject="Reset your Password",
        body=text_content,
        from_email="Videoflix@mail.com",
        to=[user.email],
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()