# Archivo: flota/views.py

from rest_framework import viewsets
from .models import Vehiculo
from .serializers import VehiculoSerializer

class VehiculoViewSet(viewsets.ModelViewSet):
    """
    Este endpoint de API permite ver y editar los vehículos.
    """
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer