from django_rq import job

from accounts_app.services.email_service import send_verification_email

from accounts_app.models import User

@job("default")
def send_verification_email_task(user_id, token):
    user = User.objects.get(pk=user_id)
    send_verification_email(user, token)