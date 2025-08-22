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
    subcategoria_details = SubcategoriaSerializer(source='subcategoria', read_only=True)
    subcategoria = serializers.PrimaryKeyRelatedField(queryset=Subcategoria.objects.all())
    modo_falla = serializers.PrimaryKeyRelatedField(queryset=ModoFalla.objects.all(), allow_null=True, required=False)
    
    class Meta:
        model = Intervencion
        fields = ['id', 'subcategoria', 'subcategoria_details', 'modo_falla', 'costo_repuestos', 'costo_mano_obra', 'notas']
        read_only_fields = ['subcategoria_details']


class OrdenTrabajoSerializer(serializers.ModelSerializer):
    intervenciones = IntervencionSerializer(many=True)
    vehiculo = serializers.PrimaryKeyRelatedField(queryset=Vehiculo.objects.all())
    vehiculo_details = VehiculoSerializer(source='vehiculo', read_only=True)

    class Meta:
        model = OrdenTrabajo
        fields = [
            'id', 'titulo', 'descripcion', 'kilometraje', 'estado', 
            'tipo_intervencion', 'fecha_creacion', 'fecha_finalizacion', 
            'intervenciones', 'vehiculo', 'vehiculo_details'
        ]
        read_only_fields = ['estado', 'fecha_creacion', 'fecha_finalizacion', 'vehiculo_details']