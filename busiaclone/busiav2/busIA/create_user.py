import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'busIA.settings')
django.setup()

from usuarios.models import Usuario

# Crear usuario normal
Usuario.objects.create_user(
    email='jpoblete@gmail.com',
    nombre='Juan Poblete',
    password='Jp123456!'
)

print("Usuario creado exitosamente")
