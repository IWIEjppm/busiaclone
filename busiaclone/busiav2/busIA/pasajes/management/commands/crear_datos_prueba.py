from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from pasajes.models import Linea, Bus, Asiento
from decimal import Decimal

class Command(BaseCommand):
    help = 'Crea datos de prueba para el sistema de pasajes'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        
        # Crear líneas
        lineas = [
            {'nombre': 'Buenos Aires - Córdoba', 'descripcion': 'Servicio directo'},
            {'nombre': 'Buenos Aires - Rosario', 'descripcion': 'Servicio semi-cama'},
            {'nombre': 'Buenos Aires - Mar del Plata', 'descripcion': 'Servicio ejecutivo'},
        ]
        
        for linea_data in lineas:
            linea = Linea.objects.create(**linea_data)
            self.stdout.write(f'Creada línea: {linea.nombre}')
            
            # Crear buses para cada línea
            for i in range(1, 4):
                bus = Bus.objects.create(
                    linea=linea,
                    numero=f'{i:03d}',
                    capacidad=20
                )
                self.stdout.write(f'Creado bus: {bus.numero} para línea {linea.nombre}')
                
                # Crear asientos para cada bus
                for j in range(1, 21):
                    precio = Decimal('1500.00') if j <= 10 else Decimal('1200.00')
                    Asiento.objects.create(
                        bus=bus,
                        numero=j,
                        estado='disponible',
                        precio=precio
                    )
                self.stdout.write(f'Creados 20 asientos para bus {bus.numero}')
        
        self.stdout.write(self.style.SUCCESS('Datos de prueba creados exitosamente'))
