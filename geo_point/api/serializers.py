from rest_framework import serializers
from points.models import LocationPoint


class LocationPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationPoint
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
