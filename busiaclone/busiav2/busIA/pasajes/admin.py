from django.contrib import admin
from .models import Pais, Region, Ciudad, Linea, Bus, Asiento, Reserva

# Register your models here.

@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre', 'codigo')

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pais')
    list_filter = ('pais',)
    search_fields = ('nombre', 'pais__nombre')

@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'region', 'latitud', 'longitud')
    list_filter = ('region__pais', 'region')
    search_fields = ('nombre', 'region__nombre', 'region__pais__nombre')

@admin.register(Linea)
class LineaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nombre_empresa', 'origen', 'destino', 'duracion', 'precio_base', 'activa')
    list_filter = ('activa', 'origen__region__pais', 'destino__region__pais', 'nombre_empresa')
    search_fields = ('nombre', 'nombre_empresa', 'origen__nombre', 'destino__nombre')

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('numero', 'linea', 'capacidad', 'activo')
    list_filter = ('activo', 'linea')
    search_fields = ('numero', 'linea__nombre')

@admin.register(Asiento)
class AsientoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'bus', 'tipo')
    list_filter = ('tipo', 'bus__linea')
    search_fields = ('numero', 'bus__numero', 'bus__linea__nombre')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'asiento', 'fecha_viaje', 'estado', 'precio')
    list_filter = ('estado', 'fecha_viaje', 'asiento__bus__linea')
    search_fields = ('usuario__username', 'asiento__bus__numero', 'asiento__bus__linea__nombre')
    date_hierarchy = 'fecha_viaje'
