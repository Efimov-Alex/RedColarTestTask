"""Файл вьюсетов."""
from rest_framework import viewsets, filters, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from points.utils import get_points_in_radius

from points.models import LocationPoint, PointMessage
from .serializers import (
    LocationPointSerializer,
    PointMessageSerializer,
    PointMessageCreateSerializer,
    RadiusSearchSerializer,
    PointMessageSearchSerializer
)


class LocationPointViewSet(viewsets.GenericViewSet,
                           mixins.ListModelMixin,
                           mixins.CreateModelMixin):
    """Вьюсет для создания точек."""

    permission_classes = [IsAuthenticated]
    queryset = LocationPoint.objects.all()
    serializer_class = LocationPointSerializer

    def get_queryset(self):
        """Получить все объекты."""
        return LocationPoint.objects.all()
    ordering_fields = ['created_at', 'name']

    @action(detail=False,
            methods=['get'],
            permission_classes=(IsAuthenticated,))
    def search(self, request):
        """Получение точек в радиусе."""
        serializer = RadiusSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        lat = serializer.validated_data['latitude']
        lon = serializer.validated_data['longitude']
        radius_km = serializer.validated_data['radius']

        points = get_points_in_radius(lat, lon, radius_km)

        return Response({
            'center_latitude': lat,
            'center_longitude': lon,
            'radius_km': radius_km,
            'points_count': len(points),
            'points': points
        })


class PointMessageViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin):
    """Вьюсет для работы с сообщениями точек."""

    queryset = PointMessage.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Получение сериализаторов."""
        if self.action == 'create':
            return PointMessageCreateSerializer
        elif self.action == 'search':
            return PointMessageSearchSerializer
        return PointMessageSerializer

    ordering_fields = ['created_at']

    def perform_create(self, serializer):
        """Сохранение пользователя."""
        serializer.save(user=self.request.user)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def search(self, request):
        """Поиск сообщений в заданном радиусе."""
        serializer = RadiusSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        lat = serializer.validated_data['latitude']
        lon = serializer.validated_data['longitude']
        radius_km = serializer.validated_data['radius']
        points_with_distance = get_points_in_radius(lat, lon, radius_km)
        if not points_with_distance:
            return Response({
                'center_latitude': lat,
                'center_longitude': lon,
                'radius_km': radius_km,
                'messages_count': 0,
                'messages': []
            })
        point_distance_map = {item['id']: item['distance_km']
                              for item in points_with_distance}
        point_ids = list(point_distance_map.keys())
        messages = PointMessage.objects.filter(point_id__in=point_ids)
        result_data = []
        for message in messages:
            message_data = PointMessageSearchSerializer(message).data
            distance = point_distance_map.get(message.point_id, 0)
            message_data['distance_km'] = round(distance, 4)
            result_data.append(message_data)
        result_data.sort(key=lambda x: x['distance_km'])

        return Response({
            'center_latitude': lat,
            'center_longitude': lon,
            'radius_km': radius_km,
            'messages_count': len(result_data),
            'messages': result_data
        })
