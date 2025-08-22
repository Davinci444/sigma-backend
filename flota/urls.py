# Archivo: flota/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehiculoViewSet

# Creamos un router que genera automáticamente las URLs para nuestro ViewSet.
router = DefaultRouter()
router.register(r'vehiculos', VehiculoViewSet, basename='vehiculo')

urlpatterns = [
    path('', include(router.urls)),
]