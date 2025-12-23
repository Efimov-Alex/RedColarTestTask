from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class LocationPoint(models.Model):
    """
    Модель для хранения географических точек без GeoDjango
    """
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
        verbose_name = "Географическая точка"
        verbose_name_plural = "Географические точки"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"
    
    def save(self, *args, **kwargs):
        if self.latitude:
            self.latitude = round(self.latitude, 6)
        if self.longitude:
            self.longitude = round(self.longitude, 6)
        super().save(*args, **kwargs)
    