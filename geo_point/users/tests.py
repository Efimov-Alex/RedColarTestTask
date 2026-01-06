"""Тесты для модели пользователя."""
import os
import django
import pytest
from django.db import IntegrityError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geo_point.settings')
django.setup()

from users.models import User


class TestUserModel:
    """Тестирование модели User."""

    @pytest.mark.django_db
    def test_create_user(self):
        """Тест создания обычного пользователя."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            phone='+79991234567'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.phone == '+79991234567'
        assert user.check_password('testpass123')
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    @pytest.mark.django_db
    def test_create_superuser(self):
        """Тест создания суперпользователя."""
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        assert admin_user.username == 'admin'
        assert admin_user.is_staff is True
        assert admin_user.is_superuser is True

    @pytest.mark.django_db
    def test_user_str_representation(self):
        """Тест строкового представления пользователя."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert str(user) == 'testuser'

    @pytest.mark.django_db
    def test_user_without_phone(self):
        """Тест создания пользователя без телефона."""
        user = User.objects.create_user(
            username='user_without_phone',
            password='testpass123'
        )
        assert user.phone == ''

    @pytest.mark.django_db
    def test_unique_username(self):
        """Тест уникальности имени пользователя."""
        User.objects.create_user(
            username='uniqueuser',
            password='testpass123'
        )
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                username='uniqueuser',
                password='anotherpass'
            )
