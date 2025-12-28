"""Файл для сериализаторов."""
from points.models import LocationPoint, PointMessage
from rest_framework import serializers


class LocationPointSerializer(serializers.ModelSerializer):
    """Сериализатор для создания точки."""

    class Meta:
        """Мета-класс."""

        model = LocationPoint
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class PointMessageCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания сообщения для точки."""

    class Meta:
        """Мета-класс."""

        model = PointMessage
        fields = ['point', 'text']

    def create(self, validated_data):
        """Добавление пользователя."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_point(self, value):
        """Валидация точки."""
        if not LocationPoint.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Точка с таким ID не существует")
        return value


class PointMessageSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения сообщений для точек."""

    user = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='user.id')
    point_name = serializers.ReadOnlyField(source='point.name')

    class Meta:
        """Мета-класс."""

        model = PointMessage
        fields = ['id', 'point', 'point_name', 'user',
                  'user_id', 'text', 'created_at']
        read_only_fields = ('user', 'created_at')


class RadiusSearchSerializer(serializers.Serializer):
    """Сериализатор для получения точек по радиусу."""

    latitude = serializers.FloatField(
        min_value=-90,
        max_value=90,
        help_text="Широта центра поиска"
    )
    longitude = serializers.FloatField(
        min_value=-180,
        max_value=180,
        help_text="Долгота центра поиска"
    )
    radius = serializers.FloatField(
        help_text="Радиус поиска в километрах"
    )


class PointMessageSearchSerializer(serializers.ModelSerializer):
    """Сериализатор для получения сообщений в  радиусе."""

    user = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='user.id')
    point_name = serializers.ReadOnlyField(source='point.name')
    point_latitude = serializers.ReadOnlyField(source='point.latitude')
    point_longitude = serializers.ReadOnlyField(source='point.longitude')
    distance_km = serializers.FloatField(read_only=True)

    class Meta:
        """Мета-класс."""

        model = PointMessage
        fields = ['id', 'point', 'point_name', 'point_latitude',
                  'point_longitude',
                  'user', 'user_id', 'text', 'created_at',
                  'distance_km']
