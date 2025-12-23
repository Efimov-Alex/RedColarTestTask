from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LocationPointViewSet

router = DefaultRouter()
router.register(r'points', LocationPointViewSet)

urlpatterns = [
    path('', include(router.urls)),
]