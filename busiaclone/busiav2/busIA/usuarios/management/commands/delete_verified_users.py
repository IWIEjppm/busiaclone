from django.core.management.base import BaseCommand
from usuarios.models import Usuario
from django.db.models import Q

class Command(BaseCommand):
    help = 'Elimina todos los usuarios verificados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            dest='dry_run',
            action='store_true',
            help='Muestra los usuarios que serían eliminados sin realizar la eliminación',
        )

    def handle(self, *args, **options):
        # Obtener usuarios verificados
        verified_users = Usuario.objects.filter(email_verificado=True)
        
        # Contar usuarios
        count = verified_users.count()
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING(f'Se encontraron {count} usuarios verificados que serían eliminados:'))
            for user in verified_users:
                self.stdout.write(f'- {user.email} (Nombre: {user.nombre})')
            self.stdout.write(self.style.SUCCESS('Operación simulada completada. No se eliminó ningún usuario.'))
        else:
            # Pedir confirmación
            self.stdout.write(self.style.WARNING(f'Se eliminarán {count} usuarios verificados.'))
            self.stdout.write(self.style.WARNING('Esta acción no se puede deshacer.'))
            
            confirm = input('¿Estás seguro que deseas continuar? [y/N]: ')
            
            if confirm.lower() == 'y':
                # Eliminar usuarios
                deleted_count = verified_users.delete()[0]
                self.stdout.write(
                    self.style.SUCCESS(f'Se eliminaron exitosamente {deleted_count} usuarios verificados.')
                )
            else:
                self.stdout.write(self.style.SUCCESS('Operación cancelada. No se eliminó ningún usuario.'))
