# Archivo: flota/views.py

from rest_framework import viewsets
from .models import Vehiculo, OrdenTrabajo, Categoria, Subcategoria, ModoFalla
from .serializers import (
    VehiculoSerializer, OrdenTrabajoSerializer, CategoriaSerializer, 
    SubcategoriaSerializer, ModoFallaSerializer
)
from django_filters.rest_framework import DjangoFilterBackend

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer

class OrdenTrabajoViewSet(viewsets.ModelViewSet):
    queryset = OrdenTrabajo.objects.all().order_by('-fecha_creacion')
    serializer_class = OrdenTrabajoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['vehiculo']

# --- NUEVOS VIEWSETS PARA EL CATÁLOGO ---
class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class SubcategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subcategoria.objects.all()
    serializer_class = SubcategoriaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['categoria']

class ModoFallaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ModoFalla.objects.all()
    serializer_class = ModoFallaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['subcategoria']