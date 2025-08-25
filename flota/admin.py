# Archivo: flota/admin.py
from django.contrib import admin
from .models import (
    Zona, Vehiculo, HistorialVehiculo,
    Categoria, Subcategoria, ModoFalla,
    OrdenTrabajo, Intervencion, Tanqueo,
    PlanMantenimiento, TareaPlan, EstadoMantenimiento,
    OrdenPreventiva, OrdenCorrectiva
)
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

# --- FUNCIÓN PARA EXPORTAR LA HOJA DE VIDA EN PDF ---
def exportar_hoja_de_vida_pdf(modeladmin, request, queryset):
    if queryset.count() != 1:
        modeladmin.message_user(request, "Por favor, seleccione solo un vehículo para exportar.", level='warning')
        return

    vehiculo = queryset.first()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="hoja_de_vida_{vehiculo.placa}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(1 * inch, height - 1 * inch, f"Hoja de Vida de Mantenimiento - {vehiculo.placa}")

    p.setFont("Helvetica", 12)
    p.drawString(1 * inch, height - 1.5 * inch, f"Vehículo: {vehiculo.marca} {vehiculo.modelo} ({vehiculo.año})")
    p.drawString(1 * inch, height - 1.7 * inch, f"Zona Actual: {vehiculo.zona.nombre}")

    y_position = height - 2.5 * inch
    ordenes = vehiculo.ordentrabajo_set.order_by('-fecha_creacion')

    p.setFont("Helvetica-Bold", 12)
    p.drawString(1 * inch, y_position, "Historial de Órdenes de Trabajo:")
    y_position -= 0.3 * inch

    for orden in ordenes:
        if y_position < 1.5 * inch:
            p.showPage()
            p.setFont("Helvetica-Bold", 12)
            y_position = height - 1 * inch

        p.setFont("Helvetica-Bold", 10)
        p.drawString(1 * inch, y_position, f"OT-{orden.id}: {orden.titulo} ({orden.fecha_creacion.strftime('%d/%m/%Y')})")
        y_position -= 0.2 * inch
        
        p.setFont("Helvetica", 9)
        p.drawString(1.2 * inch, y_position, f"Estado: {orden.get_estado_display()} | Tipo: {orden.get_tipo_intervencion_display()} | Kilometraje: {orden.kilometraje} km")
        y_position -= 0.2 * inch

        total_costo_orden = 0
        for intervencion in orden.intervenciones.all():
            costo_intervencion = intervencion.costo_repuestos + intervencion.costo_mano_obra
            total_costo_orden += costo_intervencion
            p.drawString(1.2 * inch, y_position, f"- Intervención: {intervencion.subcategoria.nombre} (Costo: ${costo_intervencion:,.2f})")
            y_position -= 0.15 * inch
        
        p.setFont("Helvetica-Bold", 9)
        p.drawString(1.2 * inch, y_position, f"Costo Total de la Orden: ${total_costo_orden:,.2f}")
        y_position -= 0.3 * inch

    p.showPage()
    p.save()
    return response
exportar_hoja_de_vida_pdf.short_description = "Exportar Hoja de Vida en PDF"


# --- CONFIGURACIÓN DEL PANEL DE ADMINISTRACIÓN ---

class TareaPlanInline(admin.TabularInline):
    model = TareaPlan
    extra = 1

@admin.register(PlanMantenimiento)
class PlanMantenimientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_motor', 'intervalo_km')
    list_filter = ('tipo_motor',)
    search_fields = ['nombre']
    inlines = [TareaPlanInline]

@admin.register(EstadoMantenimiento)
class EstadoMantenimientoAdmin(admin.ModelAdmin):
    list_display = ('vehiculo', 'ultimo_plan_realizado', 'km_ultimo_mantenimiento', 'km_proximo_mantenimiento')
    readonly_fields = ('vehiculo', 'ultimo_plan_realizado', 'km_ultimo_mantenimiento', 'km_proximo_mantenimiento')
    search_fields = ['vehiculo__placa']

@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ['nombre']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ['nombre']

@admin.register(Subcategoria)
class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria')
    list_filter = ('categoria',)
    search_fields = ['nombre', 'categoria__nombre']

@admin.register(ModoFalla)
class ModoFallaAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'subcategoria')
    list_filter = ('subcategoria__categoria', 'subcategoria')
    search_fields = ['descripcion']

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'marca', 'modelo', 'zona', 'tipo_motor')
    search_fields = ('placa', 'marca', 'modelo')
    list_filter = ('zona', 'marca', 'tipo_motor')
    actions = [exportar_hoja_de_vida_pdf]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        user_groups = request.user.groups.values_list('name', flat=True)
        return qs.filter(zona__nombre__in=list(user_groups))

    def save_model(self, request, obj, form, change):
        if change and 'zona' in form.changed_data:
            old_zona = Zona.objects.get(pk=form.initial.get('zona'))
            HistorialVehiculo.objects.create(
                vehiculo=obj,
                descripcion=f"El vehículo fue transferido de la zona '{old_zona.nombre}' a '{obj.zona.nombre}'.",
                usuario=request.user
            )
        super().save_model(request, obj, form, change)

class IntervencionCorrectivaInline(admin.TabularInline):
    model = Intervencion
    extra = 1
    autocomplete_fields = ['subcategoria', 'modo_falla']
    verbose_name_plural = "Intervenciones Correctivas (Fallas)"

class OrdenTrabajoAdminBase(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'vehiculo', 'kilometraje', 'estado')
    list_filter = ('estado', 'vehiculo__zona', 'asignado_a')
    date_hierarchy = 'fecha_creacion'
    search_fields = ['titulo', 'descripcion', 'vehiculo__placa']
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        is_newly_completed = obj.estado == 'COMPLETADA' and 'estado' in form.changed_data
        
        # Solo ejecutamos la lógica si la orden es PREVENTIVA y se acaba de COMPLETAR
        if obj.tipo_intervencion == 'PREVENTIVO' and is_newly_completed and obj.plan_aplicado:
            plan = obj.plan_aplicado
            
            # Actualizamos o creamos el estado de mantenimiento. Esta es la lógica para CUALQUIER preventivo.
            estado_mtto, created = EstadoMantenimiento.objects.update_or_create(
                vehiculo=obj.vehiculo,
                defaults={
                    'ultimo_plan_realizado': plan,
                    'km_ultimo_mantenimiento': obj.kilometraje,
                    'km_proximo_mantenimiento': obj.kilometraje + plan.intervalo_km
                }
            )

            # Si 'created' es True, significa que este fue el primer mantenimiento, por lo tanto, el plan se activó.
            if created:
                descripcion_historial = f"PLAN DE MANTENIMIENTO ACTIVADO con '{plan.nombre}'. Próximo servicio a los {estado_mtto.km_proximo_mantenimiento} km."
            else:
                descripcion_historial = f"Mantenimiento preventivo '{plan.nombre}' completado. Próximo servicio a los {estado_mtto.km_proximo_mantenimiento} km."
            
            HistorialVehiculo.objects.create(
                vehiculo=obj.vehiculo,
                descripcion=descripcion_historial,
                usuario=request.user
            )

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('vehiculo')
        if request.user.is_superuser:
            return qs
        user_groups = request.user.groups.values_list('name', flat=True)
        return qs.filter(vehiculo__zona__nombre__in=list(user_groups))

@admin.register(OrdenPreventiva)
class OrdenPreventivaAdmin(OrdenTrabajoAdminBase):
    fields = ('vehiculo', 'titulo', 'descripcion', 'kilometraje', 'asignado_a', 'estado', 'plan_aplicado')
    autocomplete_fields = ['vehiculo', 'asignado_a', 'plan_aplicado']

    def get_queryset(self, request):
        return OrdenTrabajo.objects.filter(tipo_intervencion='PREVENTIVO')
    
    def save_model(self, request, obj, form, change):
        obj.tipo_intervencion = 'PREVENTIVO'
        super().save_model(request, obj, form, change)

@admin.register(OrdenCorrectiva)
class OrdenCorrectivaAdmin(OrdenTrabajoAdminBase):
    fields = ('vehiculo', 'titulo', 'descripcion', 'kilometraje', 'asignado_a', 'estado')
    inlines = [IntervencionCorrectivaInline]

    def get_queryset(self, request):
        return OrdenTrabajo.objects.filter(tipo_intervencion='CORRECTIVO')

    def save_model(self, request, obj, form, change):
        obj.tipo_intervencion = 'CORRECTIVO'
        super().save_model(request, obj, form, change)

@admin.register(HistorialVehiculo)
class HistorialVehiculoAdmin(admin.ModelAdmin):
    list_display = ('vehiculo', 'descripcion', 'usuario', 'fecha')
    list_filter = ('vehiculo__zona', 'vehiculo')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        user_groups = request.user.groups.values_list('name', flat=True)
        return qs.filter(vehiculo__zona__nombre__in=list(user_groups))

    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request):
        return False
        
@admin.register(Intervencion)
class IntervencionAdmin(admin.ModelAdmin):
    list_display = ('id', 'orden_trabajo', 'subcategoria', 'costo_repuestos', 'costo_mano_obra')
    autocomplete_fields = ['subcategoria', 'modo_falla']

@admin.register(Tanqueo)
class TanqueoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'vehiculo', 'kilometraje', 'galones', 'costo_total')
    list_filter = ('vehiculo__zona', 'vehiculo')
    search_fields = ('vehiculo__placa',)
    date_hierarchy = 'fecha'
    autocomplete_fields = ['vehiculo']