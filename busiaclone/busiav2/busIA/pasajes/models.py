from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Pais(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=2, unique=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'País'
        verbose_name_plural = 'Países'
        ordering = ['nombre']

class Region(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.nombre}, {self.pais}"
    
    class Meta:
        verbose_name = 'Región'
        verbose_name_plural = 'Regiones'
        ordering = ['pais', 'nombre']

class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    def __str__(self):
        return f"{self.nombre}, {self.region}"
    
    class Meta:
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
        ordering = ['region', 'nombre']

class Linea(models.Model):
    nombre = models.CharField(max_length=100)
    nombre_empresa = models.CharField(max_length=100)
    origen = models.ForeignKey(Ciudad, on_delete=models.PROTECT, related_name='lineas_origen')
    destino = models.ForeignKey(Ciudad, on_delete=models.PROTECT, related_name='lineas_destino')
    duracion = models.DurationField(help_text='Duración estimada del viaje')
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    activa = models.BooleanField(default=True, db_index=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.nombre_empresa}"
    
    class Meta:
        verbose_name = 'Línea'
        verbose_name_plural = 'Líneas'
        ordering = ['nombre_empresa', 'nombre']

class Bus(models.Model):
    linea = models.ForeignKey(Linea, on_delete=models.CASCADE)
    numero = models.CharField(max_length=20)
    capacidad = models.PositiveIntegerField()
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Bus {self.numero} - {self.linea}"
    
    class Meta:
        verbose_name = 'Bus'
        verbose_name_plural = 'Buses'
        ordering = ['linea', 'numero']
        unique_together = ['linea', 'numero']

class Viaje(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    fecha_salida = models.DateTimeField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    estado = models.CharField(max_length=20, choices=[
        ('programado', 'Programado'),
        ('en_ruta', 'En Ruta'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado')
    ], default='programado')

    def __str__(self):
        return f"{self.bus.linea.nombre} - {self.fecha_salida}"

    class Meta:
        verbose_name = 'Viaje'
        verbose_name_plural = 'Viajes'
        ordering = ['fecha_salida']

class Asiento(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    numero = models.PositiveIntegerField()
    tipo = models.CharField(max_length=20, choices=[
        ('normal', 'Normal'),
        ('premium', 'Premium'),
    ], default='normal')
    
    def __str__(self):
        return f"Asiento {self.numero} - {self.bus}"
    
    class Meta:
        verbose_name = 'Asiento'
        verbose_name_plural = 'Asientos'
        ordering = ['bus', 'numero']
        unique_together = ['bus', 'numero']

class Reserva(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    asiento = models.ForeignKey(Asiento, on_delete=models.CASCADE)
    fecha_viaje = models.DateField()
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ])
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    paypal_order_id = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"Reserva {self.id} - {self.usuario} - {self.asiento}"
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha_reserva']
