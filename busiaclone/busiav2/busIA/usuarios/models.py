from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import RegexValidator
import random
import string
import secrets

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        
        # Eliminar espacios del email
        email = self.normalize_email(email.strip())
        
        # Validar que el email no contenga espacios
        if ' ' in email:
            raise ValueError('El email no puede contener espacios')
            
        usuario = self.model(email=email, nombre=nombre.strip(), **extra_fields)
        if password:
            # Validar que la contraseña no contenga espacios
            if ' ' in password:
                raise ValueError('La contraseña no puede contener espacios')
            usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, nombre, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, nombre, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    # Validador para teléfono
    telefono_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="El número debe estar en formato: '+999999999'. Mínimo 9 y máximo 15 dígitos."
    )

    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=255)
    telefono = models.CharField(
        validators=[telefono_validator],
        max_length=15,
        blank=True,
        null=True,
        help_text="Formato: +56912345678"
    )
    email_alternativo = models.EmailField(blank=True, null=True)
    foto_perfil = models.ImageField(
        upload_to='usuarios/fotos_perfil/', 
        null=True, 
        blank=True,
        help_text='Foto de perfil del usuario'
    )
    is_active = models.BooleanField(default=True)
    email_verificado = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    codigo_verificacion = models.CharField(max_length=6, blank=True, null=True)
    expiracion_verificacion = models.DateTimeField(null=True, blank=True)
    codigo_recuperacion = models.CharField(max_length=6, blank=True, null=True)
    fecha_codigo_recuperacion = models.DateTimeField(null=True, blank=True)
    
    # Campos para recuperación de cuenta
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    reset_token_created = models.DateTimeField(blank=True, null=True)
    
    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.email

    def clean(self):
        self.email = self.email.strip() if self.email else None
        self.nombre = self.nombre.strip() if self.nombre else None
        if self.telefono:
            self.telefono = self.telefono.strip()
        if self.email_alternativo:
            self.email_alternativo = self.email_alternativo.strip()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def generar_codigo_verificacion(self):
        """Genera un código de verificación y establece su tiempo de expiración."""
        codigo = ''.join(random.choices(string.digits, k=6))
        self.codigo_verificacion = codigo
        self.expiracion_verificacion = timezone.now() + timezone.timedelta(minutes=2)
        self.save()
        return codigo

    def verificar_email(self, codigo):
        """Verifica el código proporcionado y actualiza el estado de verificación."""
        if not self.codigo_verificacion or not self.expiracion_verificacion:
            return False, "No hay un código de verificación pendiente"

        if timezone.now() > self.expiracion_verificacion:
            return False, "El código ha expirado"

        if codigo != self.codigo_verificacion:
            return False, "Código incorrecto"

        self.is_verified = True
        self.codigo_verificacion = None
        self.expiracion_verificacion = None
        self.save()
        return True, "Email verificado correctamente"

    def generar_codigo_recuperacion(self):
        """Genera un código de recuperación y establece su tiempo de expiración."""
        codigo = ''.join(random.choices(string.digits, k=6))  # Genera un código de 6 dígitos
        self.codigo_recuperacion = codigo
        self.fecha_codigo_recuperacion = timezone.now()
        self.save()
        return codigo

    def verificar_codigo_recuperacion(self, codigo):
        """Verifica el código de recuperación proporcionado."""
        if not self.codigo_recuperacion or not self.fecha_codigo_recuperacion:
            return False, "No hay un código de recuperación pendiente"

        tiempo_transcurrido = timezone.now() - self.fecha_codigo_recuperacion
        if tiempo_transcurrido.total_seconds() > 120:  # 2 minutos
            return False, "El código ha expirado"

        if codigo != self.codigo_recuperacion:
            return False, "Código incorrecto"

        return True, "Código verificado correctamente"

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
