# Archivo: flota/models.py
from django.db import models
from django.contrib.auth.models import User


# --- MODELOS DE CATÁLOGO DINÁMICO ---

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name = "Categoría de Mantenimiento"
        verbose_name_plural = "Categorías de Mantenimiento"

class Subcategoria(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, verbose_name="Categoría")
    nombre = models.CharField(max_length=150, verbose_name="Nombre de la Subcategoría")
    def __str__(self):
        return f"{self.categoria.nombre} -> {self.nombre}"
    class Meta:
        verbose_name = "Subcategoría"
        verbose_name_plural = "Subcategorías"
        unique_together = ('categoria', 'nombre')

class ModoFalla(models.Model):
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.CASCADE, verbose_name="Subcategoría Asociada")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción del Modo de Falla")
    def __str__(self):
        return self.descripcion
    class Meta:
        verbose_name = "Modo de Falla"
        verbose_name_plural = "Modos de Falla"

# --- MODELOS OPERACIONALES ---

class Zona(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nombre

class Vehiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True, verbose_name="Placa")
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    año = models.PositiveIntegerField(verbose_name="Año")
    zona = models.ForeignKey(Zona, on_delete=models.PROTECT, verbose_name="Zona de Operación")
    
    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.placa}"

class OrdenTrabajo(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, verbose_name="Vehículo")
    asignado_a = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Gestor Asignado")
    titulo = models.CharField(max_length=200, verbose_name="Título de la Orden")
    descripcion = models.TextField(verbose_name="Descripción General")
    kilometraje = models.PositiveIntegerField(verbose_name="Kilometraje al momento del Mantenimiento")

    ESTADO_CHOICES = [
        ('ABIERTA', 'Abierta'),
        ('EN_PROGRESO', 'En Progreso'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ABIERTA')

    INTERVENCION_CHOICES = [
        ('PREVENTIVO', 'Mantenimiento Preventivo'),
        ('CORRECTIVO', 'Mantenimiento Correctivo'),
    ]
    tipo_intervencion = models.CharField(max_length=20, choices=INTERVENCION_CHOICES)

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_finalizacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Finalización")

    def __str__(self):
        return f"OT-{self.id}: {self.titulo} para {self.vehiculo.placa}"
    class Meta:
        verbose_name = "Orden de Trabajo"
        verbose_name_plural = "Órdenes de Trabajo"

class Intervencion(models.Model):
    orden_trabajo = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name='intervenciones')
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.PROTECT, verbose_name="Tarea/Componente")
    modo_falla = models.ForeignKey(ModoFalla, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Modo de Falla (si aplica)")
    costo_repuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    costo_mano_obra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notas = models.TextField(blank=True, null=True, verbose_name="Notas de la Intervención")
    def __str__(self):
        return f"Intervención en {self.subcategoria.nombre} para OT-{self.orden_trabajo.id}"

# --- MODELOS DE REGISTRO Y AUDITORÍA ---

class HistorialVehiculo(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, verbose_name="Vehículo")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del Evento")
    descripcion = models.TextField(verbose_name="Descripción del Evento")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario Responsable")
    def __str__(self):
        return f"Log para {self.vehiculo.placa} en {self.fecha.strftime('%Y-%m-%d')}"
    class Meta:
        ordering = ['-fecha']

class Tanqueo(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, verbose_name="Vehículo")
    fecha = models.DateTimeField(verbose_name="Fecha y Hora del Tanqueo")
    kilometraje = models.PositiveIntegerField(verbose_name="Kilometraje")
    galones = models.DecimalField(max_digits=8, decimal_places=3, verbose_name="Galones")
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Costo Total ($)")
    conductor = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return f"Tanqueo para {self.vehiculo.placa} el {self.fecha.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Registro de Tanqueo"
        verbose_name_plural = "Registros de Tanqueo"
        ordering = ['-fecha']