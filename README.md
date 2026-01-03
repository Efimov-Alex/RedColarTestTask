# Django GeoPoints API

Backend-приложение на Django для работы с географическими точками на карте. Приложение предоставляет REST API для создания точек, обмена сообщениями и поиска контента в заданном радиусе от указанных координат.

## Технический стек

- Python 3.10+
- Django 5.0+
- Django REST Framework 3.15+
- Django REST Framework Simple JWT 5.3.0+
- Djoser 2.2.0+
- geopy 2.4.0+ (для гео-расчетов)
- SQLite (для разработки)

## Основные функции

1. **Создание географических точек** (POST /api/points/)
2. **Создание сообщений к точкам** (POST /api/points/messages/)
3. **Поиск точек в радиусе** (GET /api/points/search/)
4. **Поиск сообщений в радиусе** (GET /api/points/messages/search/)
5. **Пагинация** для всех списковых эндпоинтов
6. **JWT аутентификация** для всех защищенных эндпоинтов

## Техническое описание проекта

### Архитектура приложения

```text
geo_point/
├── api/ # Основной модуль API
│ ├── views.py # ViewSets и обработчики запросов
│ ├── serializers.py # Сериализаторы для моделей
│ ├── urls.py # Маршруты API
│ └── tests/ # Тесты API
├── points/ # Модуль географических точек
│ ├── models.py # Модели LocationPoint и PointMessage
│ ├── utils.py # Утилиты для гео-расчетов
│ └── tests/ # Тесты моделей и утилит
├── users/ # Модуль пользователей
│ ├── models.py # Кастомная модель User
│ └── tests/ # Тесты пользователей
└── geo_point/ # Конфигурация проекта
├── settings.py # Настройки Django
├── urls.py # Главные URL маршруты
└── wsgi.py # WSGI конфигурация
```


### Модели данных

#### 1. User (Пользователь)
- Наследуется от AbstractUser Django
- Добавлено поле phone для хранения телефона
- Поддерживает стандартную аутентификацию Django

#### 2. LocationPoint (Географическая точка)
- Содержит координаты (широта, долгота) с валидацией диапазонов
- Включает название, описание и адрес
- Автоматическое округление координат до 6 знаков
- Индексы для оптимизации поиска по координатам и дате создания

#### 3. PointMessage (Сообщение точки)
- Связь многие-к-одному с LocationPoint
- Связь многие-к-одному с User
- Содержит текст сообщения и метаданные
- Индексы для оптимизации запросов по точкам и пользователям

### Географические расчеты

Приложение использует библиотеку geopy для точных географических расчетов:

- **Метод расчета**: Формула гаверсинусов (Haversine formula) через функцию geodesic
- **Точность**: Расчет расстояний между точками на поверхности сферы
- **Единицы измерения**: Все расстояния возвращаются в километрах
- **Валидация координат**: Широта от -90 до 90°, долгота от -180 до 180°

### Алгоритм поиска в радиусе

1. Получение всех точек из базы данных через Django ORM
2. Расчет расстояния от центра поиска до каждой точки с помощью функции get_distance
3. Фильтрация точек по заданному радиусу (<= radius_km)
4. Сортировка результатов по расстоянию (от ближней к дальней)
5. Применение пагинации к отфильтрованному списку
6. Возврат результатов с метаданными (расстояние, координаты, информация о точке)

### Безопасность

- **Аутентификация**: JWT (JSON Web Tokens) через библиотеку Simple JWT
  - Access токен: 7 дней
  - Refresh токен: 30 дней
  - Автоматическая ротация refresh токенов
- **Авторизация**: Все эндпоинты защищены требованием аутентификации через IsAuthenticated permission
- **Валидация данных**:
  - Координаты проверяются на корректность диапазона
  - Все строковые поля проходят стандартную валидацию Django
  - Защита от SQL-инъекций через использование ORM Django
- **Защита от атак**:
  - CSRF защита для сессионной аутентификации
  - Валидация паролей через стандартные валидаторы Django
  - Безопасное хранение секретных ключей

### Тестирование

Проект включает комплексные тесты с использованием pytest
Для запуска тестов:

```bash
# Установка тестовых зависимостей
pip install pytest pytest-django pytest-cov

# Запуск всех тестов
pytest

# Запуск тестов с покрытием
pytest --cov=.

# Запуск конкретных тестов
pytest users/tests.py
pytest points/tests.py
pytest api/tests.py
```


## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd geo-points-api
```
### 2. Создание виртуального окружения

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Применение миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 6. Запуск сервера разработки

```bash
python manage.py runserver
```

## API Документация

### Аутентификация

Все эндпоинты (кроме аутентификации) требуют JWT токен.
#### Получение токена:

Запрос:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

Ответ:

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Обновление токена

```bash
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "your_refresh_token"}'
```

### Эндпоинты API

#### Создание точки (POST /api/points/)

Запрос:

```bash
curl -X POST http://127.0.0.1:8000/api/points/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Красная площадь",
    "description": "Главная площадь Москвы",
    "latitude": 55.753900,
    "longitude": 37.620800,
    "address": "Москва, Красная площадь, 1"
  }'
```

Ответ:

```json
{
  "id": 1,
  "name": "Красная площадь",
  "description": "Главная площадь Москвы",
  "latitude": "55.753900",
  "longitude": "37.620800",
  "address": "Москва, Красная площадь, 1",
  "created_at": "2025-12-30T11:57:36.975610Z",
  "updated_at": "2025-12-30T11:57:36.975610Z"
}
```

#### Получение списка точек (GET /api/points/)

Запрос:

```bash
curl -X GET "http://127.0.0.1:8000/api/points/" \
  -H "Authorization: Bearer <access_token>"
```

Ответ:

```json
[
    {
        "id": 1,
        "name": "Красная площадь",
        "description": "Главная площадь Москвы",
        "latitude": "55.753900",
        "longitude": "37.620800",
        "address": "Москва, Красная площадь, 1",
        "created_at": "2025-12-30T11:57:36.975610Z",
        "updated_at": "2025-12-30T11:57:36.975610Z"
    }
]
```

#### Поиск точек в радиусе (GET /api/points/search/)

Запрос:

```bash
curl -X GET "http://127.0.0.1:8000/api/points/search/?latitude=55.7558&longitude=37.6176&radius=5" \
  -H "Authorization: Bearer <access_token>"
```

Ответ:

```json
{
    "center": {
        "latitude": 55.7558,
        "longitude": 37.6176
    },
    "radius_km": 5.0,
    "count": 1,
    "points": [
        {
            "id": 1,
            "name": "Красная площадь",
            "description": "Главная площадь Москвы",
            "latitude": 55.7539,
            "longitude": 37.6208,
            "address": "Москва, Красная площадь, 1",
            "created_at": "2025-12-30T11:57:36.975610+00:00",
            "updated_at": "2025-12-30T11:57:36.975610+00:00",
            "distance_km": 0.2917498556208802
        }
    ]
}
```

#### Создание сообщения (POST /api/points/messages/)

Запрос:

```bash
curl -X POST http://127.0.0.1:8000/api/points/messages/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "point": 1,
    "text": "Красивое место! Рекомендую посетить на закате."
  }'
```

Ответ:

```json
{
    "point": 1,
    "text": "Красивое место! Рекомендую посетить на закате."
}
```

#### Получение сообщений (GET /api/points/messages/)

Запрос:

```bash
curl -X GET "http://127.0.0.1:8000/api/points/messages" \
  -H "Authorization: Bearer <access_token>"
```

Ответ:

```json
[
    {
        "id": 2,
        "point": 1,
        "point_name": "Красная площадь",
        "point_latitude": 55.7539,
        "point_longitude": 37.6208,
        "user": "admin",
        "user_id": 1,
        "text": "Красивое место! Рекомендую посетить на закате.",
        "created_at": "2026-01-01T12:48:16.825569Z"
    },
    {
        "id": 1,
        "point": 1,
        "point_name": "Красная площадь",
        "point_latitude": 55.7539,
        "point_longitude": 37.6208,
        "user": "admin",
        "user_id": 1,
        "text": "Очень красивое место!",
        "created_at": "2025-12-30T11:59:38.273265Z"
    }
]
```

#### Поиск сообщений в радиусе (GET /api/points/messages/search/)

Запрос:

```bash
curl -X GET "http://127.0.0.1:8000/api/points/messages/search/?latitude=55.7558&longitude=37.6176&radius=5" \
  -H "Authorization: Bearer <access_token>"
```

Ответ:

```json
{
    "center": {
        "latitude": 55.7558,
        "longitude": 37.6176
    },
    "radius_km": 5.0,
    "count": 2,
    "messages": [
        {
            "id": 2,
            "point": 1,
            "point_name": "Красная площадь",
            "point_latitude": 55.7539,
            "point_longitude": 37.6208,
            "user": "admin",
            "user_id": 1,
            "text": "Красивое место! Рекомендую посетить на закате.",
            "created_at": "2026-01-01T12:48:16.825569Z",
            "distance_km": 0.2917
        },
        {
            "id": 1,
            "point": 1,
            "point_name": "Красная площадь",
            "point_latitude": 55.7539,
            "point_longitude": 37.6208,
            "user": "admin",
            "user_id": 1,
            "text": "Очень красивое место!",
            "created_at": "2025-12-30T11:59:38.273265Z",
            "distance_km": 0.2917
        }
    ]
}
```
