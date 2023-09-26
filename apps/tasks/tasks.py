from django.template.loader import render_to_string
from apps.accounts.models import User
from apps.tasks.serializers import UserTasksSerializer
from celery import shared_task
from django.core.mail import EmailMessage
from config import settings
from email.mime.text import MIMEText


def send_email_to_user(user):
    user_email = user.get('email')
    message_body = render_to_string('email_body.html', user)
    message = EmailMessage(
        subject='Assigned tasks',
        from_email=settings.EMAIL_HOST_USER,
        to=[user_email],
    )
    body = MIMEText(message_body, 'html')
    message.attach(body)
    message.send()


@shared_task(bind=True)
def send_mail_func(self):
    users = User.objects.prefetch_related('assigns')

    users_tasks = UserTasksSerializer(users, many=True).data

    for user in users_tasks:
        send_email_to_user(user)

    return "Success"

