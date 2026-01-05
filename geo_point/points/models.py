"""Основные модели."""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class LocationPoint(models.Model):
    """Модель для хранения географических точек."""

    name = models.CharField(
        max_length=255,
        verbose_name="Название точки"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание"
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name="Широта",
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ],
        help_text="Широта в градусах от -90 до 90"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name="Долгота",
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ],
        help_text="Долгота в градусах от -180 до 180"
    )
    address = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Адрес"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        """Мета-класс."""

        verbose_name = "Географическая точка"
        verbose_name_plural = "Географические точки"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        """Представление в виде строки."""
        return f"{self.name} ({self.latitude}, {self.longitude})"

    def save(self, *args, **kwargs):
        """Сохранение."""
        if self.latitude:
            self.latitude = round(self.latitude, 6)
        if self.longitude:
            self.longitude = round(self.longitude, 6)
        super().save(*args, **kwargs)


class PointMessage(models.Model):
    """Модель для сообщений, привязанных к географической точке."""

    point = models.ForeignKey(
        LocationPoint,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Точка"
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='point_messages',
        verbose_name="Пользователь"
    )
    text = models.TextField(
        verbose_name="Текст сообщения"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        """Мета-класс."""

        verbose_name = "Сообщение точки"
        verbose_name_plural = "Сообщения точек"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['point', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        """Представление в виде строки."""
        return f"Сообщение от {self.user.username} к точке {self.point.name}"
