# Archivo: flota/views.py

from rest_framework import viewsets
from .models import Vehiculo, OrdenTrabajo # <-- Añadir OrdenTrabajo
from .serializers import VehiculoSerializer, OrdenTrabajoSerializer # <-- Añadir OrdenTrabajoSerializer
from django_filters.rest_framework import DjangoFilterBackend # <-- Añadir para filtros

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer

# --- NUEVA CLASE AÑADIDA ---
class OrdenTrabajoViewSet(viewsets.ModelViewSet):
    queryset = OrdenTrabajo.objects.all().order_by('-fecha_creacion')
    serializer_class = OrdenTrabajoSerializer
    filter_backends = [DjangoFilterBackend] # <-- Activar filtros
    filterset_fields = ['vehiculo'] # <-- Permitir filtrar por vehículo