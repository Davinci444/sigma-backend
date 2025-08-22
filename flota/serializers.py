# Archivo: flota/serializers.py

from rest_framework import serializers
from .models import Vehiculo, Zona, OrdenTrabajo, Intervencion, Subcategoria, Categoria

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
        fields = ['nombre']

class SubcategoriaSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    class Meta:
        model = Subcategoria
        fields = ['nombre', 'categoria']

class IntervencionSerializer(serializers.ModelSerializer):
    subcategoria = SubcategoriaSerializer(read_only=True)
    class Meta:
        model = Intervencion
        fields = ['id', 'subcategoria', 'costo_repuestos', 'costo_mano_obra']

class OrdenTrabajoSerializer(serializers.ModelSerializer):
    intervenciones = IntervencionSerializer(many=True, read_only=True)
    # Le decimos que al crear, espere recibir solo el ID (la llave primaria) del vehículo.
    vehiculo = serializers.PrimaryKeyRelatedField(queryset=Vehiculo.objects.all())

    class Meta:
        model = OrdenTrabajo
        fields = [
            'id', 'titulo', 'descripcion', 'kilometraje', 'estado', 
            'tipo_intervencion', 'fecha_creacion', 'fecha_finalizacion', 'intervenciones',
            'vehiculo' # Campo añadido para la creación/escritura
        ]
        # Definimos campos que no se deben poder escribir directamente al crear,
        # ya que se gestionan de forma automática.
        read_only_fields = ['estado', 'fecha_creacion', 'fecha_finalizacion', 'intervenciones']