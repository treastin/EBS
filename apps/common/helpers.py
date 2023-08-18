from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

from django.core.mail import send_mail as mail_template

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v1",
        description="Enjoy",
    ),
    public=True,
    permission_classes=[AllowAny],
)


def send_mail(user, subject='Empty', message='Empty'):
    if user is None:
        return

    mail_template(
        subject,
        message,
        'EBS.test@example.com',
        [user],
        fail_silently=True,
    )
