from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django_rq import job


def send_verification_email(user, token):
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