# Archivo: flota/serializers.py

from rest_framework import serializers
from .models import (
    Vehiculo, Zona, OrdenTrabajo, Intervencion, 
    Subcategoria, Categoria, ModoFalla
)

class ZonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zona
        fields = ['nombre']

class VehiculoSerializer(serializers.ModelSerializer):
    zona = ZonaSerializer(read_only=True)
    class Meta:
        model = Vehiculo
        fields = ['id', 'placa', 'marca', 'modelo', 'año', 'zona']

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']

class SubcategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategoria
        fields = ['id', 'nombre', 'categoria']

class ModoFallaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModoFalla
        fields = ['id', 'descripcion', 'subcategoria']

class IntervencionSerializer(serializers.ModelSerializer):
    subcategoria = SubcategoriaSerializer(read_only=True)
    class Meta:
        model = Intervencion
        fields = ['id', 'subcategoria', 'costo_repuestos', 'costo_mano_obra']

class OrdenTrabajoSerializer(serializers.ModelSerializer):
    intervenciones = IntervencionSerializer(many=True, read_only=True)
    vehiculo = serializers.PrimaryKeyRelatedField(queryset=Vehiculo.objects.all())
    # Hacemos que el serializador muestre los detalles del vehículo al leer
    vehiculo_details = VehiculoSerializer(source='vehiculo', read_only=True)

    class Meta:
        model = OrdenTrabajo
        fields = [
            'id', 'titulo', 'descripcion', 'kilometraje', 'estado', 
            'tipo_intervencion', 'fecha_creacion', 'fecha_finalizacion', 
            'intervenciones', 'vehiculo', 'vehiculo_details'
        ]
        read_only_fields = ['estado', 'fecha_creacion', 'fecha_finalizacion', 'intervenciones', 'vehiculo_details']