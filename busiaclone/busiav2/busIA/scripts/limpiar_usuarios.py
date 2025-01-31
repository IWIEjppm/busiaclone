import os
import sys
import django

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'busIA.settings')
django.setup()

from usuarios.models import Usuario
from django.db import transaction

def limpiar_usuarios():
    """Elimina todas las cuentas de usuario excepto superusuarios."""
    try:
        with transaction.atomic():
            # Eliminar usuarios que no son superusuarios
            usuarios_eliminados = Usuario.objects.filter(is_superuser=False).delete()
            print(f"Se eliminaron {usuarios_eliminados[0]} usuarios.")
    except Exception as e:
        print(f"Error al eliminar usuarios: {str(e)}")

if __name__ == '__main__':
    limpiar_usuarios()
