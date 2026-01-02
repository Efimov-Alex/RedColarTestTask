"""Файл для фильтров."""
from django_filters import rest_framework as filters
from points.models import LocationPoint, PointMessage


class LocationPointFilter(filters.FilterSet):
    """Фильтр для географических точек."""
    
    name = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = LocationPoint
        fields = ['name', 'description']


class PointMessageFilter(filters.FilterSet):
    """Фильтр для сообщений точек."""
    
    text = filters.CharFilter(lookup_expr='icontains')
    user = filters.NumberFilter(field_name='user__id')
    point = filters.NumberFilter(field_name='point__id')
    
    class Meta:
        model = PointMessage
        fields = ['text', 'user', 'point']