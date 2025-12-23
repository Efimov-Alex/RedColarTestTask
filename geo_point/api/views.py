from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from points.models import LocationPoint
from .serializers import LocationPointSerializer

class LocationPointViewSet(viewsets.ModelViewSet):
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