from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Добавьте кастомные поля если нужно
    phone = models.CharField(max_length=15, blank=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'