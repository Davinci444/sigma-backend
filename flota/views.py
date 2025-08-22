# Archivo: flota/views.py

from rest_framework import viewsets, status
from .models import Vehiculo, OrdenTrabajo, Categoria, Subcategoria, ModoFalla
from .serializers import (
    VehiculoSerializer, OrdenTrabajoSerializer, CategoriaSerializer, 
    SubcategoriaSerializer, ModoFallaSerializer, IntervencionSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer

class OrdenTrabajoViewSet(viewsets.ModelViewSet):
    queryset = OrdenTrabajo.objects.all().order_by('-fecha_creacion')
    serializer_class = OrdenTrabajoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['vehiculo']

    def create(self, request, *args, **kwargs):
        intervenciones_data = request.data.pop('intervenciones', [])
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        orden_trabajo = serializer.save()

        for intervencion_data in intervenciones_data:
            intervencion_data['orden_trabajo'] = orden_trabajo.id
            intervencion_serializer = IntervencionSerializer(data=intervencion_data)
            intervencion_serializer.is_valid(raise_exception=True)
            intervencion_serializer.save()

        # Re-serializamos la instancia completa para devolver el objeto anidado
        final_serializer = self.get_serializer(orden_trabajo)
        headers = self.get_success_headers(final_serializer.data)
        return Response(final_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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