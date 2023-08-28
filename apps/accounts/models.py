from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone


class User(AbstractBaseUser):
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(
        default=True,
        help_text=
        "Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
    )
    date_joined = models.DateTimeField("date joined", default=timezone.now)

    USERNAME_FIELD = "email"

    objects = UserManager()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"



