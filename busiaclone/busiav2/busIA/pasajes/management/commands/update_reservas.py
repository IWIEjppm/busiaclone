from django.core.management.base import BaseCommand
from pasajes.models import Reserva

class Command(BaseCommand):
    help = 'Actualiza todas las reservas pendientes a confirmadas'

    def handle(self, *args, **options):
        # Obtener todas las reservas pendientes
        reservas = Reserva.objects.filter(estado='pendiente')
        count = reservas.count()
        
        # Actualizar a confirmadas
        reservas.update(estado='confirmada')
        
        self.stdout.write(
            self.style.SUCCESS(f'Se actualizaron {count} reservas a estado confirmada')
        )
