"""Модель пользователя."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    phone = models.CharField(max_length=15, blank=True)

    class Meta:
        """Мета-класс."""

        verbose_name = 'User'
        verbose_name_plural = 'Users'
