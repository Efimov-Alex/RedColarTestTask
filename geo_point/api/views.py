from rest_framework import viewsets, filters, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
import math

from points.models import LocationPoint, PointMessage
from .serializers import (
    LocationPointSerializer, 
    PointMessageSerializer,
    PointMessageCreateSerializer,
)

class LocationPointViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin):
    queryset = LocationPoint.objects.all()
    
    def get_serializer_class(self):
        return LocationPointSerializer
    

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ['name']
    search_fields = ['name', 'description', 'address']
    ordering_fields = ['created_at', 'name']

class PointMessageViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Вьюсет для работы с сообщениями точек.
    Поддерживает только GET (список и детали) и POST (создание)
    """
    queryset = PointMessage.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PointMessageCreateSerializer
        return PointMessageSerializer
    
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ['point', 'user']
    search_fields = ['text']
    ordering_fields = ['created_at']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    