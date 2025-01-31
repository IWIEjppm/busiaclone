"""
Vistas para la gestión de pasajes y viajes
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from datetime import datetime, timedelta
import json
import logging

from .models import Linea, Bus, Asiento, Reserva, Ciudad, Viaje
from .services import UbicacionService

logger = logging.getLogger(__name__)

@login_required
def comprar(request):
    """Vista para la página de compra de pasajes."""
    return render(request, 'pasajes/comprar.html', {
        'fecha_minima': datetime.now().date().strftime('%Y-%m-%d')
    })

@login_required
def index(request):
    """Vista principal de la aplicación."""
    return redirect('comprar')

# @login_required  # Temporalmente comentado para debug
def buscar_ciudades(request):
    """API para buscar ciudades por nombre."""
    try:
        query = request.GET.get('q', '')
        logger.debug(f"Buscando ciudades con query: {query}")
        
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        ciudades = Ciudad.objects.filter(
            Q(nombre__icontains=query) | 
            Q(region__nombre__icontains=query) |
            Q(region__pais__nombre__icontains=query)
        ).select_related('region', 'region__pais')[:10]
        
        logger.debug(f"SQL Query: {ciudades.query}")
        logger.debug(f"Ciudades encontradas: {list(ciudades)}")
        
        results = [{
            'id': ciudad.id,
            'text': f"{ciudad.nombre}, {ciudad.region.nombre}, {ciudad.region.pais.nombre}"
        } for ciudad in ciudades]
        
        return JsonResponse({'results': results})
    except Exception as e:
        logger.error(f"Error en buscar_ciudades: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def buscar_viajes_api(request):
    """API para buscar viajes disponibles."""
    origen_id = request.GET.get('origen')
    destino_id = request.GET.get('destino')
    fecha_str = request.GET.get('fecha')
    
    if not all([origen_id, destino_id, fecha_str]):
        return JsonResponse({
            'error': 'Faltan parámetros requeridos'
        }, status=400)
    
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        if fecha < datetime.now().date():
            raise ValueError('La fecha no puede ser anterior a hoy')
    except ValueError as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)
    
    # Buscar viajes disponibles para la fecha
    viajes_disponibles = Viaje.objects.filter(
        bus__linea__origen_id=origen_id,
        bus__linea__destino_id=destino_id,
        fecha_salida__date=fecha,
        estado='programado'
    ).select_related(
        'bus__linea',
        'bus__linea__origen',
        'bus__linea__destino'
    ).order_by('fecha_salida')
    
    viajes = []
    for viaje in viajes_disponibles:
        asientos_disponibles = Asiento.objects.filter(
            bus=viaje.bus,
            reserva__isnull=True
        ).count()
        
        if asientos_disponibles > 0:
            viajes.append({
                'viaje_id': viaje.id,
                'bus_id': viaje.bus.id,
                'empresa': viaje.bus.linea.nombre_empresa,
                'origen': str(viaje.bus.linea.origen),
                'destino': str(viaje.bus.linea.destino),
                'hora_salida': viaje.fecha_salida.strftime('%H:%M'),
                'duracion': str(viaje.bus.linea.duracion),
                'precio': float(viaje.precio),
                'asientos_disponibles': asientos_disponibles
            })
    
    return JsonResponse({'viajes': viajes})

@login_required
def obtener_asientos_api(request, viaje_id):
    """API para obtener el estado de los asientos de un viaje."""
    try:
        viaje = Viaje.objects.get(id=viaje_id, estado='programado')
        # Obtener asientos y sus reservas para la fecha del viaje
        asientos = Asiento.objects.filter(bus=viaje.bus)
        reservas = Reserva.objects.filter(
            asiento__in=asientos,
            fecha_viaje=viaje.fecha_salida.date(),
            estado='confirmada'
        ).values_list('asiento_id', flat=True)
        
        asientos_data = []
        for asiento in asientos:
            asientos_data.append({
                'id': asiento.id,
                'numero': asiento.numero,
                'tipo': asiento.tipo,
                'ocupado': asiento.id in reservas
            })
        
        return JsonResponse({
            'viaje': {
                'id': viaje.id,
                'empresa': viaje.bus.linea.nombre_empresa,
                'origen': str(viaje.bus.linea.origen),
                'destino': str(viaje.bus.linea.destino),
                'fecha_salida': viaje.fecha_salida.strftime('%Y-%m-%d %H:%M'),
                'precio': float(viaje.precio)
            },
            'asientos': asientos_data
        })
    except Viaje.DoesNotExist:
        return JsonResponse({'error': 'Viaje no encontrado'}, status=404)
    except Exception as e:
        logger.error(f"Error en obtener_asientos_api: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def crear_reserva(request):
    """API para crear una reserva."""
    try:
        data = json.loads(request.body)
        asiento_id = data.get('asiento_id')
        fecha_str = data.get('fecha_viaje')
        
        if not all([asiento_id, fecha_str]):
            raise ValueError('Faltan parámetros requeridos')
        
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        if fecha < datetime.now().date():
            raise ValueError('La fecha no puede ser anterior a hoy')
        
        # Verificar que el asiento esté disponible
        asiento = get_object_or_404(Asiento, id=asiento_id)
        if Reserva.objects.filter(
            asiento=asiento,
            fecha_viaje=fecha,
            estado='confirmada'
        ).exists():
            raise ValueError('El asiento ya está reservado')
        
        # Obtener el viaje y su precio
        viaje = get_object_or_404(
            Viaje,
            bus=asiento.bus,
            fecha_salida__date=fecha,
            estado='programado'
        )
        
        # Crear reserva confirmada
        reserva = Reserva.objects.create(
            usuario=request.user,
            asiento=asiento,
            fecha_viaje=fecha,
            estado='confirmada',
            precio=viaje.precio
        )
        
        logger.info(f"Reserva {reserva.id} creada para {request.user}")
        
        return JsonResponse({
            'reserva_id': reserva.id,
            'precio': float(reserva.precio)
        })
        
    except ValueError as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Error al crear reserva: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'Error al crear la reserva'
        }, status=500)

@login_required
@require_http_methods(['POST'])
def confirmar_pago(request, reserva_id):
    """API para confirmar el pago de una reserva."""
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        
        if not order_id:
            raise ValueError('Falta el ID de la orden de PayPal')
        
        reserva = get_object_or_404(
            Reserva,
            id=reserva_id,
            usuario=request.user,
            estado='pendiente'
        )
        
        # Aquí deberíamos verificar el pago con PayPal
        # Por ahora solo actualizamos el estado
        reserva.estado = 'confirmada'
        reserva.paypal_order_id = order_id
        reserva.save()
        
        return JsonResponse({'status': 'ok'})
        
    except ValueError as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'Error al confirmar el pago'
        }, status=500)

@login_required
def mis_viajes(request):
    """Vista para mostrar los viajes del usuario."""
    reservas = Reserva.objects.filter(
        usuario=request.user,
        estado='confirmada'
    ).select_related(
        'asiento',
        'asiento__bus',
        'asiento__bus__linea',
        'asiento__bus__linea__origen',
        'asiento__bus__linea__destino'
    ).order_by('-fecha_viaje')
    
    logger.debug(f"Reservas encontradas para {request.user}: {reservas.count()}")
    
    return render(request, 'pasajes/mis_viajes.html', {
        'reservas': reservas
    })
