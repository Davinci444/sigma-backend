from django import template
from flota.models import OrdenTrabajo, Vehiculo, Intervencion, Categoria
from django.db.models import Count, Sum
from django.utils import timezone
import datetime
import json

register = template.Library()

@register.simple_tag
def get_dashboard_stats():
    hoy = timezone.now()
    inicio_de_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # --- Cálculos de Estadísticas (como antes) ---
    ordenes_abiertas = OrdenTrabajo.objects.filter(estado__in=['ABIERTA', 'EN_PROGRESO']).count()
    ordenes_cerradas_mes = OrdenTrabajo.objects.filter(
        estado='COMPLETADA',
        fecha_finalizacion__gte=inicio_de_mes
    ).count()
    total_vehiculos = Vehiculo.objects.count()
    correctivos_mes = OrdenTrabajo.objects.filter(
        tipo_intervencion='CORRECTIVO',
        fecha_creacion__gte=inicio_de_mes
    ).count()
    preventivos_mes = OrdenTrabajo.objects.filter(
        tipo_intervencion='PREVENTIVO',
        fecha_creacion__gte=inicio_de_mes
    ).count()

    # --- NUEVO CÁLCULO PARA EL GRÁFICO ---
    # Agrupamos todas las intervenciones por su categoría principal y sumamos sus costos.
    costos_por_categoria = Intervencion.objects.values('subcategoria__categoria__nombre').annotate(
        costo_total=Sum('costo_repuestos') + Sum('costo_mano_obra')
    ).order_by('-costo_total')

    # Preparamos los datos para que JavaScript los entienda
    chart_labels = [item['subcategoria__categoria__nombre'] for item in costos_por_categoria]
    chart_data = [float(item['costo_total']) for item in costos_por_categoria]

    return {
        'total_vehiculos': total_vehiculos,
        'ordenes_abiertas_totales': ordenes_abiertas,
        'ordenes_cerradas_este_mes': ordenes_cerradas_mes,
        'correctivos_este_mes': correctivos_mes,
        'preventivos_este_mes': preventivos_mes,
        # Pasamos los datos del gráfico, convertidos a formato JSON para seguridad
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    