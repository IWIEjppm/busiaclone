from django.core.management.base import BaseCommand
from pasajes.models import Bus, Asiento

class Command(BaseCommand):
    help = 'Genera asientos para todos los buses'

    def handle(self, *args, **kwargs):
        buses = Bus.objects.all()
        asientos_creados = 0

        for bus in buses:
            # Crear 40 asientos por bus (10 filas de 4 asientos)
            for i in range(1, 41):
                tipo = 'premium' if i <= 8 else 'normal'  # Primeros 8 asientos son premium
                Asiento.objects.get_or_create(
                    bus=bus,
                    numero=i,
                    defaults={'tipo': tipo}
                )
                asientos_creados += 1

        self.stdout.write(
            self.style.SUCCESS(f'Se crearon {asientos_creados} asientos exitosamente')
        )
