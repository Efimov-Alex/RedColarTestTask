"""Тесты для API endpoints."""
import os
import django
import pytest
from rest_framework import status

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geo_point.settings')
django.setup()

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
from points.models import LocationPoint, PointMessage


@pytest.fixture
def api_client():
    """Фикстура для API клиента."""
    return APIClient()


@pytest.fixture
def test_user():
    """Фикстура для тестового пользователя."""
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Фикстура для аутентифицированного клиента."""
    refresh = RefreshToken.for_user(test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def location_point():
    """Фикстура для тестовой точки."""
    return LocationPoint.objects.create(
        name='Тестовая точка',
        latitude=55.7539,
        longitude=37.6208,
        description='Описание тестовой точки',
        address='Тестовый адрес'
    )


@pytest.fixture
def point_message(test_user, location_point):
    """Фикстура для тестового сообщения."""
    return PointMessage.objects.create(
        point=location_point,
        user=test_user,
        text='Тестовое сообщение'
    )


class TestAuthentication:
    """Тесты аутентификации."""

    @pytest.mark.django_db
    def test_get_jwt_token(self, api_client, test_user):
        """Тест получения JWT токена."""
        url = '/api/token/'
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    @pytest.mark.django_db
    def test_refresh_jwt_token(self, api_client, test_user):
        """Тест обновления JWT токена."""
        url = '/api/token/'
        data = {'username': 'testuser', 'password': 'testpass123'}
        token_response = api_client.post(url, data, format='json')
        refresh_token = token_response.data['refresh']
        url = '/api/token/refresh/'
        data = {'refresh': refresh_token}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data


class TestLocationPointAPI:
    """Тесты API для географических точек."""

    @pytest.mark.django_db
    def test_create_point_unauthorized(self, api_client):
        """Тест создания точки без авторизации."""
        url = '/api/points/'
        data = {
            'name': 'Неавторизованная точка',
            'latitude': 55.7539,
            'longitude': 37.6208
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_create_point_authorized(self, authenticated_client):
        """Тест создания точки с авторизацией."""
        url = '/api/points/'
        data = {
            'name': 'Тестовая точка API',
            'latitude': 55.7539,
            'longitude': 37.6208,
            'description': 'Описание точки',
            'address': 'Адрес точки'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']
        assert response.data['latitude'] == '55.753900'
        assert response.data['longitude'] == '37.620800'

    @pytest.mark.django_db
    def test_create_point_invalid_coordinates(self, authenticated_client):
        """Тест создания точки с некорректными координатами."""
        url = '/api/points/'
        data = {
            'name': 'Точка с ошибкой',
            'latitude': 100.0,
            'longitude': 200.0
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_list_points(self, authenticated_client, location_point):
        """Тест получения списка точек."""
        url = '/api/points/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    @pytest.mark.django_db
    def test_search_points_in_radius(self, authenticated_client,
                                     location_point):
        """Тест поиска точек в радиусе."""
        url = '/api/points/search/'
        params = {
            'latitude': 55.7540,
            'longitude': 37.6210,
            'radius': 1
        }
        response = authenticated_client.get(url, params)
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'points' in response.data
        assert response.data['count'] >= 1

    @pytest.mark.django_db
    def test_search_points_invalid_params(self, authenticated_client):
        """Тест поиска с некорректными параметрами."""
        url = '/api/points/search/'
        params = {
            'latitude': 'invalid',
            'longitude': 37.6210,
            'radius': 1
        }
        response = authenticated_client.get(url, params)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestPointMessageAPI:
    """Тесты API для сообщений точек."""

    @pytest.mark.django_db
    def test_create_message_unauthorized(self, api_client, location_point):
        """Тест создания сообщения без авторизации."""
        url = '/api/points/messages/'
        data = {
            'point': location_point.id,
            'text': 'Неавторизованное сообщение'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_create_message_authorized(self, authenticated_client,
                                       location_point):
        """Тест создания сообщения с авторизацией."""
        url = '/api/points/messages/'
        data = {
            'point': location_point.id,
            'text': 'Тестовое сообщение API'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['text'] == data['text']
        assert response.data['point'] == location_point.id

    @pytest.mark.django_db
    def test_create_message_invalid_point(self, authenticated_client):
        """Тест создания сообщения для несуществующей точки."""
        url = '/api/points/messages/'
        data = {
            'point': 999,
            'text': 'Сообщение'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_list_messages(self, authenticated_client, point_message):
        """Тест получения списка сообщений."""
        url = '/api/points/messages/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    @pytest.mark.django_db
    def test_search_messages_in_radius(self, authenticated_client,
                                       location_point, point_message):
        """Тест поиска сообщений в радиусе."""
        url = '/api/points/messages/search/'
        params = {
            'latitude': location_point.latitude,
            'longitude': location_point.longitude,
            'radius': 1
        }
        response = authenticated_client.get(url, params)
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'messages' in response.data
        assert response.data['count'] >= 1

    @pytest.mark.django_db
    def test_message_contains_user_info(self, authenticated_client,
                                        test_user, point_message):
        """Тест, что сообщение содержит информацию о пользователе."""
        url = '/api/points/messages/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        message_data = response.data[0]
        assert 'user' in message_data
        assert message_data['user'] == test_user.username
        assert 'user_id' in message_data
        assert message_data['user_id'] == test_user.id


class TestAPIValidation:
    """Тесты валидации API."""

    @pytest.mark.django_db
    def test_radius_search_validation(self, authenticated_client):
        """Тест валидации параметров поиска по радиусу."""
        url = '/api/points/search/'
        params = {'latitude': 100, 'longitude': 37.6, 'radius': 10}
        response = authenticated_client.get(url, params)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        params = {'latitude': 55.75, 'longitude': 200, 'radius': 10}
        response = authenticated_client.get(url, params)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        params = {'latitude': 55.75, 'longitude': 37.6}
        response = authenticated_client.get(url, params)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
