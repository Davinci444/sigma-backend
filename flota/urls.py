# Archivo: flota/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehiculoViewSet
from .views import VehiculoViewSet, OrdenTrabajoViewSet

# Creamos un router que genera automáticamente las URLs para nuestro ViewSet.
router = DefaultRouter()
router.register(r'vehiculos', VehiculoViewSet, basename='vehiculo')
router.register(r'ordenes', OrdenTrabajoViewSet, basename='ordentrabajo')

urlpatterns = [
    path('', include(router.urls)),
]