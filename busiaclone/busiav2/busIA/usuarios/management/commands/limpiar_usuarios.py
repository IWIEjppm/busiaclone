from django.core.management.base import BaseCommand
from usuarios.models import Usuario
from django.utils import timezone

class Command(BaseCommand):
    help = 'Elimina usuarios no verificados y/o inactivos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Elimina todos los usuarios excepto superusuarios',
        )
        parser.add_argument(
            '--no-verificados',
            action='store_true',
            help='Elimina solo usuarios no verificados',
        )

    def handle(self, *args, **options):
        if options['all']:
            # Eliminar todos los usuarios excepto superusuarios
            usuarios = Usuario.objects.filter(is_superuser=False)
            count = usuarios.count()
            usuarios.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Se eliminaron {count} usuarios')
            )
        
        elif options['no_verificados']:
            # Eliminar usuarios no verificados
            usuarios = Usuario.objects.filter(email_verificado=False)
            count = usuarios.count()
            usuarios.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Se eliminaron {count} usuarios no verificados')
            )
        
        else:
            # Eliminar usuarios no verificados y expirados
            usuarios = Usuario.objects.filter(
                email_verificado=False,
                expiracion_verificacion__lt=timezone.now()
            )
            count = usuarios.count()
            usuarios.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Se eliminaron {count} usuarios expirados')
            )
