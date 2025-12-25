from geopy.distance import geodesic
from .models import LocationPoint

def get_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km

def get_points_in_radius(lat, lon, radius_km):
    points = LocationPoint.objects.all()

    points_in_radius = []
    for point in points:
        distance = get_distance(lat, lon, float(point.latitude), float(point.longitude))

        if distance <= radius_km:
            points_in_radius.append({
                'id': point.id,
                'name': point.name,
                'description': point.description,
                'latitude': float(point.latitude),
                'longitude': float(point.longitude),
                'address': point.address,
                'created_at': point.created_at.isoformat() if point.created_at else None,
                'updated_at': point.updated_at.isoformat() if point.updated_at else None,
                'distance_km': distance
            })
            
    points_in_radius.sort(key=lambda x: x['distance_km'])

    return points_in_radius
