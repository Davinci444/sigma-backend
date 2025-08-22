from rest_framework import serializers
from .models import Vehiculo, Zona

class ZonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zona
        fields = ['nombre']

class VehiculoSerializer(serializers.ModelSerializer):
    # Le decimos que use el 'traductor' de Zona para mostrar el nombre de la zona, no solo su ID.
    zona = ZonaSerializer(read_only=True)

    class Meta:
        model = Vehiculo
        # Estos son los campos que nuestro 'traductor' expondrá.
        fields = ['id', 'placa', 'marca', 'modelo', 'año', 'zona']