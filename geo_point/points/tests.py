"""Тесты для моделей точек и утилит."""
import os
import django
import pytest
from django.core.exceptions import ValidationError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geo_point.settings')
django.setup()

from points.models import LocationPoint, PointMessage
from points.utils import get_distance, get_points_in_radius
from users.models import User


@pytest.fixture
def test_user():
    """Фикстура для тестового пользователя."""
    return User.objects.create_user(
        username='testuser',
        password='testpass123'
    )


@pytest.fixture
def moscow_point():
    """Фикстура для точки в Москве."""
    return LocationPoint.objects.create(
        name='Москва, Красная площадь',
        latitude=55.7539,
        longitude=37.6208,
        description='Главная площадь Москвы',
        address='Москва, Красная площадь'
    )


@pytest.fixture
def spb_point():
    """Фикстура для точки в Санкт-Петербурге."""
    return LocationPoint.objects.create(
        name='Санкт-Петербург, Эрмитаж',
        latitude=59.9398,
        longitude=30.3146,
        description='Государственный Эрмитаж',
        address='Санкт-Петербург, Дворцовая площадь'
    )


class TestLocationPointModel:
    """Тестирование модели LocationPoint."""

    @pytest.mark.django_db
    def test_create_location_point(self, moscow_point):
        """Тест создания географической точки."""
        assert moscow_point.name == 'Москва, Красная площадь'
        assert moscow_point.latitude == 55.753900
        assert moscow_point.longitude == 37.620800
        assert moscow_point.description == 'Главная площадь Москвы'
        assert moscow_point.created_at is not None

    @pytest.mark.django_db
    def test_location_point_str(self, moscow_point):
        """Тест строкового представления точки."""
        expected_str = "Москва, Красная площадь (55.7539, 37.6208)"
        assert str(moscow_point) == expected_str

    @pytest.mark.django_db
    def test_location_point_validation_valid(self):
        """Тест валидации корректных координат."""
        point = LocationPoint(
            name='Тест',
            latitude=45.0,
            longitude=90.0
        )
        point.full_clean()
        
    @pytest.mark.django_db
    def test_location_point_validation_invalid_latitude(self):
        """Тест валидации некорректной широты."""
        point = LocationPoint(
            name='Тест',
            latitude=100.0,
            longitude=90.0
        )
        with pytest.raises(ValidationError):
            point.full_clean()
            
    @pytest.mark.django_db
    def test_location_point_validation_invalid_longitude(self):
        """Тест валидации некорректной долготы."""
        point = LocationPoint(
            name='Тест',
            latitude=45.0,
            longitude=200.0
        )
        with pytest.raises(ValidationError):
            point.full_clean()


class TestPointMessageModel:
    """Тестирование модели PointMessage."""
    
    @pytest.mark.django_db
    def test_create_point_message(self, test_user, moscow_point):
        """Тест создания сообщения к точке."""
        message = PointMessage.objects.create(
            point=moscow_point,
            user=test_user,
            text='Тестовое сообщение'
        )
        
        assert message.point == moscow_point
        assert message.user == test_user
        assert message.text == 'Тестовое сообщение'
        assert message.created_at is not None
        
    @pytest.mark.django_db
    def test_point_message_str(self, test_user, moscow_point):
        """Тест строкового представления сообщения."""
        message = PointMessage.objects.create(
            point=moscow_point,
            user=test_user,
            text='Тестовое сообщение'
        )
        
        expected_str = f"Сообщение от {test_user.username} к точке {moscow_point.name}"
        assert str(message) == expected_str
        
    @pytest.mark.django_db
    def test_message_related_to_point(self, test_user, moscow_point):
        """Тест связи сообщения с точкой."""
        PointMessage.objects.create(
            point=moscow_point,
            user=test_user,
            text='Сообщение 1'
        )
        PointMessage.objects.create(
            point=moscow_point,
            user=test_user,
            text='Сообщение 2'
        )
        
        assert moscow_point.messages.count() == 2
        assert all(msg.point == moscow_point for msg in moscow_point.messages.all())


class TestUtils:
    """Тестирование утилитных функций."""
    
    def test_get_distance_same_point(self):
        """Тест расстояния между одинаковыми точками."""
        distance = get_distance(55.7539, 37.6208, 55.7539, 37.6208)
        assert distance == 0.0
        
    def test_get_distance_moscow_to_spb(self):
        """Тест расстояния Москва -> Санкт-Петербург."""
        distance = get_distance(55.7558, 37.6173, 59.9343, 30.3351)
        assert 600 < distance < 650
        
    @pytest.mark.django_db
    def test_get_points_in_radius_empty(self, moscow_point, spb_point):
        """Тест поиска точек в радиусе (пустой результат)."""
        center_lat, center_lon = 55.7540, 37.6210
        points = get_points_in_radius(center_lat, center_lon, 0.1)
        
        assert len(points) == 1
        assert points[0]['name'] == 'Москва, Красная площадь'
        
    @pytest.mark.django_db
    def test_get_points_in_radius_with_results(self, moscow_point, spb_point):
        """Тест поиска точек в радиусе (есть результаты)."""
        points = get_points_in_radius(55.7558, 37.6173, 700)
        
        assert len(points) == 2
        assert points[0]['distance_km'] <= points[1]['distance_km']
        assert points[0]['name'] == 'Москва, Красная площадь'
        
    @pytest.mark.django_db
    def test_get_points_in_radius_fields(self, moscow_point):
        """Тест полей возвращаемых точек."""
        points = get_points_in_radius(55.7539, 37.6208, 1)  
        assert len(points) == 1
        point_data = points[0]
        expected_fields = {
            'id', 'name', 'description', 'latitude', 'longitude',
            'address', 'created_at', 'updated_at', 'distance_km'
        }
        assert set(point_data.keys()) == expected_fields
        assert point_data['distance_km'] == 0.0
