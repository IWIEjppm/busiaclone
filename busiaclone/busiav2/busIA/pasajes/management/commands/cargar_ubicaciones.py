"""
Comando para cargar ubicaciones desde APIs externas
"""

from django.core.management.base import BaseCommand
from pasajes.services import UbicacionService

class Command(BaseCommand):
    help = 'Carga países, regiones y ciudades desde APIs externas'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando carga de ubicaciones...')
        
        try:
            contador = UbicacionService.actualizar_ubicaciones()
            
            self.stdout.write(self.style.SUCCESS(
                f'Carga completada exitosamente:\n'
                f'- Países creados/actualizados: {contador["paises"]}\n'
                f'- Regiones creadas/actualizadas: {contador["regiones"]}\n'
                f'- Ciudades creadas/actualizadas: {contador["ciudades"]}'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error durante la carga: {str(e)}'))
