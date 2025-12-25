from rest_framework import serializers
from points.models import LocationPoint, PointMessage


class LocationPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationPoint
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class PointMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointMessage
        fields = ['point', 'text']
    
    def validate_point(self, value):
        if not LocationPoint.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Точка с таким ID не существует")
        return value
    
class PointMessageSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='user.id')
    point_name = serializers.ReadOnlyField(source='point.name')
    
    class Meta:
        model = PointMessage
        fields = ['id', 'point', 'point_name', 'user', 'user_id', 'text', 'created_at']
        read_only_fields = ('user', 'created_at')

class RadiusSearchSerializer(serializers.Serializer):
    latitude = serializers.FloatField(
        help_text="Широта центра поиска"
    )
    longitude = serializers.FloatField(
        help_text="Долгота центра поиска"
    )
    radius = serializers.FloatField(
        help_text="Радиус поиска в километрах"
    )