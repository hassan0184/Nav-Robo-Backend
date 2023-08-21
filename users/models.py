from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=32, null=True, blank=True)

    OPERATOR = 1
    RIDER = 2

    ROLE_CHOICES = (
        (OPERATOR, 'Operator'),
        (RIDER, 'Rider'),
    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
