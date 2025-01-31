"""
Servicios para la gestión de ubicaciones y búsqueda de viajes
"""

import requests
from typing import List, Dict, Any
from django.conf import settings
from .models import Pais, Region, Ciudad

class UbicacionService:
    """
    Servicio para gestionar la obtención y actualización de ubicaciones
    utilizando APIs externas
    """
    
    @staticmethod
    def obtener_paises() -> List[Dict[str, Any]]:
        """
        Obtiene la lista de países desde la API de RestCountries
        Returns:
            List[Dict]: Lista de países con su información
        """
        url = "https://restcountries.com/v3.1/all"
        response = requests.get(url)
        response.raise_for_status()
        
        paises = []
        for pais in response.json():
            if 'name' in pais and 'cca2' in pais:
                paises.append({
                    'nombre': pais['name']['common'],
                    'codigo': pais['cca2']
                })
        
        return sorted(paises, key=lambda x: x['nombre'])

    @staticmethod
    def obtener_ciudades(pais_codigo: str) -> List[Dict[str, Any]]:
        """
        Obtiene las ciudades de un país usando la API de GeoDB Cities
        Args:
            pais_codigo: Código ISO del país
        Returns:
            List[Dict]: Lista de ciudades con su información
        """
        url = f"https://wft-geo-db.p.rapidapi.com/v1/geo/cities"
        headers = {
            "X-RapidAPI-Key": settings.GEODB_API_KEY,
            "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
        }
        params = {
            "countryIds": pais_codigo,
            "minPopulation": 100000,  # Solo ciudades con más de 100,000 habitantes
            "types": "CITY",
            "sort": "-population"  # Ordenar por población descendente
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        ciudades = []
        for ciudad in response.json()['data']:
            ciudades.append({
                'nombre': ciudad['city'],
                'region': ciudad['region'],
                'latitud': ciudad['latitude'],
                'longitud': ciudad['longitude']
            })
        
        return ciudades

    @classmethod
    def actualizar_ubicaciones(cls) -> Dict[str, int]:
        """
        Actualiza la base de datos con la información de países y ciudades
        Returns:
            Dict: Contador de elementos creados/actualizados
        """
        contador = {'paises': 0, 'regiones': 0, 'ciudades': 0}
        
        # 1. Obtener y actualizar países
        paises = cls.obtener_paises()
        for pais_data in paises:
            pais, created = Pais.objects.update_or_create(
                codigo=pais_data['codigo'],
                defaults={'nombre': pais_data['nombre']}
            )
            if created:
                contador['paises'] += 1
            
            # 2. Obtener y actualizar ciudades del país
            try:
                ciudades = cls.obtener_ciudades(pais.codigo)
                for ciudad_data in ciudades:
                    # Crear o actualizar región
                    region, created = Region.objects.update_or_create(
                        nombre=ciudad_data['region'],
                        pais=pais,
                        defaults={'nombre': ciudad_data['region']}
                    )
                    if created:
                        contador['regiones'] += 1
                    
                    # Crear o actualizar ciudad
                    ciudad, created = Ciudad.objects.update_or_create(
                        nombre=ciudad_data['nombre'],
                        region=region,
                        defaults={
                            'latitud': ciudad_data['latitud'],
                            'longitud': ciudad_data['longitud']
                        }
                    )
                    if created:
                        contador['ciudades'] += 1
                        
            except Exception as e:
                print(f"Error al obtener ciudades de {pais.nombre}: {str(e)}")
                continue
        
        return contador


class ViajeService:
    """
    Servicio para la búsqueda y gestión de viajes
    """
    
    @staticmethod
    def buscar_viajes(origen_id: int, destino_id: int, fecha: str) -> List[Dict[str, Any]]:
        """
        Busca viajes disponibles según origen, destino y fecha
        Args:
            origen_id: ID de la ciudad de origen
            destino_id: ID de la ciudad de destino
            fecha: Fecha del viaje en formato YYYY-MM-DD
        Returns:
            List[Dict]: Lista de viajes disponibles con su información
        """
        from django.db.models import Count, Q
        from .models import Linea
        
        # Buscar líneas que coincidan con origen y destino
        lineas = Linea.objects.filter(
            origen_id=origen_id,
            destino_id=destino_id
        ).select_related(
            'empresa',
            'origen',
            'destino'
        ).prefetch_related(
            'buses__asientos'
        ).annotate(
            asientos_disponibles=Count(
                'buses__asientos',
                filter=Q(buses__asientos__estado='disponible')
            )
        )
        
        viajes = []
        for linea in lineas:
            for bus in linea.buses.all():
                viajes.append({
                    'linea_id': linea.id,
                    'empresa': linea.empresa.nombre,
                    'origen': linea.origen.nombre,
                    'destino': linea.destino.nombre,
                    'duracion': str(linea.duracion),
                    'precio_base': float(linea.precio_base),
                    'bus_id': bus.id,
                    'bus_numero': bus.numero,
                    'asientos_disponibles': sum(1 for a in bus.asientos.all() if a.estado == 'disponible')
                })
        
        return sorted(viajes, key=lambda x: x['precio_base'])
