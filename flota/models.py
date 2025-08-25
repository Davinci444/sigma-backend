# Archivo: flota/models.py

from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre
    class Meta: verbose_name_plural = "Categorías de Mantenimiento"

class Subcategoria(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=150)
    def __str__(self): return f"{self.categoria.nombre} -> {self.nombre}"
    class Meta: verbose_name_plural = "Subcategorías"; unique_together = ('categoria', 'nombre')

class ModoFalla(models.Model):
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=255)
    def __str__(self): return self.descripcion
    class Meta: verbose_name_plural = "Modos de Falla"

class Zona(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre

class Vehiculo(models.Model):
    TIPO_MOTOR_CHOICES = [('GASOLINA', 'Gasolina'), ('DIESEL', 'Diesel')]
    placa = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    año = models.PositiveIntegerField()
    zona = models.ForeignKey(Zona, on_delete=models.PROTECT)
    tipo_motor = models.CharField(max_length=10, choices=TIPO_MOTOR_CHOICES, default='GASOLINA')
    def __str__(self): return f"{self.marca} {self.modelo} - {self.placa}"

class OrdenTrabajo(models.Model):
    ESTADO_CHOICES = [('ABIERTA', 'Abierta'), ('EN_PROGRESO', 'En Progreso'), ('COMPLETADA', 'Completada'), ('CANCELADA', 'Cancelada')]
    INTERVENCION_CHOICES = [('PREVENTIVO', 'Mantenimiento Preventivo'), ('CORRECTIVO', 'Mantenimiento Correctivo')]
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    asignado_a = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    kilometraje = models.PositiveIntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ABIERTA')
    tipo_intervencion = models.CharField(max_length=20, choices=INTERVENCION_CHOICES)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    class Meta: verbose_name_plural = "Órdenes de Trabajo"

class Intervencion(models.Model):
    orden_trabajo = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name='intervenciones')
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.PROTECT)
    modo_falla = models.ForeignKey(ModoFalla, on_delete=models.PROTECT, null=True, blank=True)
    costo_repuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    costo_mano_obra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notas = models.TextField(blank=True, null=True)

class EstadoMantenimiento(models.Model):
    vehiculo = models.OneToOneField(Vehiculo, on_delete=models.CASCADE, primary_key=True)
    km_activacion = models.PositiveIntegerField(default=0, help_text="Kilometraje en el que se activó el plan por primera vez.")
    km_ultimo_mantenimiento = models.PositiveIntegerField(default=0, help_text="Kilometraje del último mantenimiento preventivo completado.")
    km_proximo_mantenimiento = models.PositiveIntegerField(default=0, help_text="Kilometraje calculado para el próximo servicio preventivo (cada 10.000km).")
    
    def __str__(self):
        return f"Estado de Mtto. para {self.vehiculo.placa}"
    class Meta:
        verbose_name_plural = "Estados de Mantenimiento"

class HistorialVehiculo(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    class Meta: ordering = ['-fecha']

class Tanqueo(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    kilometraje = models.PositiveIntegerField()
    galones = models.DecimalField(max_digits=8, decimal_places=3)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    conductor = models.CharField(max_length=150, null=True, blank=True)
    class Meta: verbose_name_plural = "Registros de Tanqueo"; ordering = ['-fecha']

class OrdenPreventiva(OrdenTrabajo):
    class Meta: proxy = True; verbose_name_plural = "Órdenes de Mantenimiento Preventivo"

class OrdenCorrectiva(OrdenTrabajo):
    class Meta: proxy = True; verbose_name_plural = "Órdenes de Mantenimiento Correctivo"