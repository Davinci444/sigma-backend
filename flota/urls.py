# Archivo: flota/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VehiculoViewSet, OrdenTrabajoViewSet, CategoriaViewSet, 
    SubcategoriaViewSet, ModoFallaViewSet
)

router = DefaultRouter()
router.register(r'vehiculos', VehiculoViewSet, basename='vehiculo')
router.register(r'ordenes', OrdenTrabajoViewSet, basename='ordentrabajo')
# --- NUEVAS RUTAS PARA EL CATÁLOGO ---
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'subcategorias', SubcategoriaViewSet, basename='subcategoria')
router.register(r'modos-falla', ModoFallaViewSet, basename='modofalla')


urlpatterns = [
    path('', include(router.urls)),
]