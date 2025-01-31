"""
Vistas para la autenticación y gestión de usuarios.
Incluye funcionalidades para registro, login, verificación y recuperación de cuenta.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from django.core.exceptions import ValidationError

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status

import json
import secrets
import string
import logging
from smtplib import SMTPException

# Configurar logging
logger = logging.getLogger(__name__)

from .models import Usuario
from pasajes.models import Reserva

def registro(request):
    """Vista para registrar un nuevo usuario."""
    if request.method == 'POST':
        try:
            # Validar datos requeridos
            nombre = request.POST.get('nombre')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
            
            if not all([nombre, email, password, password2]):
                messages.error(request, 'Todos los campos son requeridos.')
                return redirect('usuarios:registro')
            
            # Validar que las contraseñas coincidan
            if password != password2:
                messages.error(request, 'Las contraseñas no coinciden.')
                return redirect('usuarios:registro')
            
            # Validar longitud de contraseña
            if len(password) < 8:
                messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
                return redirect('usuarios:registro')
            
            # Verificar si el email ya está registrado
            if Usuario.objects.filter(email=email).exists():
                messages.error(request, 'Este email ya está registrado.')
                return redirect('usuarios:registro')
            
            # Crear el usuario
            usuario = Usuario.objects.create_user(
                email=email,
                password=password,
                nombre=nombre,
                is_active=False  # El usuario estará inactivo hasta verificar su email
            )
            
            # Generar código de verificación
            codigo = usuario.generar_codigo_verificacion()
            
            # Enviar email de verificación
            try:
                subject = 'Verifica tu cuenta en BusIA'
                html_message = render_to_string('usuarios/emails/verificacion.html', {
                    'usuario': usuario,
                    'codigo': codigo
                })
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                # Guardar el email en la sesión para el proceso de verificación
                request.session['usuario_pendiente_verificacion'] = email
                
                messages.success(
                    request, 
                    'Te hemos enviado un código de verificación a tu correo. '
                    'Por favor, verifica tu cuenta para poder iniciar sesión.'
                )
                return redirect('usuarios:verificar_email')
                
            except SMTPException as e:
                logger.error(f'Error al enviar email de verificación: {str(e)}')
                usuario.delete()  # Eliminar el usuario si falla el envío
                messages.error(
                    request, 
                    'Ha ocurrido un error al enviar el email de verificación. '
                    'Por favor, intenta nuevamente.'
                )
                return redirect('usuarios:registro')
                
        except Exception as e:
            logger.error(f'Error en registro: {str(e)}')
            messages.error(request, 'Ha ocurrido un error. Por favor intenta nuevamente.')
            return redirect('usuarios:registro')
    
    return render(request, 'usuarios/registro.html')

def verificar_email(request):
    """Vista para verificar el email del usuario."""
    if not request.session.get('usuario_pendiente_verificacion'):
        messages.error(request, 'No hay ninguna cuenta pendiente de verificación.')
        return redirect('usuarios:login')
    
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        email = request.session.get('usuario_pendiente_verificacion')
        
        if not codigo:
            messages.error(request, 'Por favor ingresa el código de verificación.')
            return redirect('usuarios:verificar_email')
        
        try:
            usuario = Usuario.objects.get(email=email, is_active=False)
            if usuario.verificar_email(codigo):
                # Limpiar la sesión
                del request.session['usuario_pendiente_verificacion']
                
                messages.success(request, '¡Tu cuenta ha sido verificada exitosamente! Ya puedes iniciar sesión.')
                return redirect('usuarios:login')
            else:
                messages.error(request, 'El código de verificación es inválido o ha expirado.')
                return redirect('usuarios:verificar_email')
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
            return redirect('usuarios:login')
        except Exception as e:
            logger.error(f'Error al verificar email: {str(e)}')
            messages.error(request, 'Ha ocurrido un error. Por favor intenta nuevamente.')
            return redirect('usuarios:verificar_email')
    
    return render(request, 'usuarios/verificar_email.html')

def reenviar_codigo(request):
    """Vista para reenviar el código de verificación."""
    email = request.session.get('usuario_pendiente_verificacion')
    if not email:
        messages.error(request, 'No hay ninguna cuenta pendiente de verificación.')
        return redirect('usuarios:login')
    
    try:
        usuario = Usuario.objects.get(email=email, is_active=False)
        codigo = usuario.generar_codigo_verificacion()
        
        # Enviar email de verificación
        subject = 'Nuevo código de verificación - BusIA'
        html_message = render_to_string('usuarios/emails/verificacion.html', {
            'usuario': usuario,
            'codigo': codigo
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=html_message,
            fail_silently=False,
        )
        
        messages.success(
            request, 
            'Te hemos enviado un nuevo código de verificación. '
            'Por favor, revisa tu correo.'
        )
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('usuarios:login')
    except SMTPException as e:
        logger.error(f'Error al reenviar código de verificación: {str(e)}')
        messages.error(
            request, 
            'Ha ocurrido un error al enviar el código. '
            'Por favor, intenta nuevamente.'
        )
    except Exception as e:
        logger.error(f'Error al reenviar código: {str(e)}')
        messages.error(request, 'Ha ocurrido un error. Por favor intenta nuevamente.')
    
    return redirect('usuarios:verificar_email')

def login_view(request):
    """Vista para iniciar sesión."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        if not email or not password:
            messages.error(request, 'Por favor ingresa tu email y contraseña.')
            return redirect('usuarios:login')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                if not remember:
                    request.session.set_expiry(0)
                
                messages.success(request, '¡Bienvenido de vuelta!')
                return redirect('usuarios:dashboard')
            else:
                messages.error(request, 'Tu cuenta no ha sido verificada. Por favor, verifica tu email.')
                return redirect('usuarios:verificar_email')
        else:
            messages.error(request, 'Email o contraseña incorrectos.')
            return redirect('usuarios:login')
    
    return render(request, 'usuarios/login.html')

@login_required
def logout_view(request):
    """Vista para cerrar sesión."""
    logout(request)
    messages.success(request, '¡Hasta pronto!')
    return redirect('usuarios:login')

@login_required
def cambiar_password(request):
    """Vista para cambiar la contraseña del usuario."""
    if request.method == 'POST':
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if not password or not password2:
            messages.error(request, 'Por favor completa todos los campos.')
            return redirect('usuarios:cambiar_password')
        
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('usuarios:cambiar_password')
        
        if len(password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return redirect('usuarios:cambiar_password')
        
        try:
            request.user.set_password(password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Contraseña actualizada exitosamente.')
            return redirect('usuarios:dashboard')
        except Exception as e:
            logger.error(f'Error al cambiar contraseña: {str(e)}')
            messages.error(request, 'Ocurrió un error al cambiar la contraseña.')
            return redirect('usuarios:cambiar_password')
    
    return render(request, 'usuarios/cambiar_password.html')

@login_required
def perfil_view(request):
    """Vista para ver y editar el perfil del usuario."""
    if request.method == 'POST':
        # Si se está actualizando la foto de perfil
        if 'foto_perfil' in request.FILES:
            try:
                # Si ya existe una foto, la borramos
                if request.user.foto_perfil:
                    request.user.foto_perfil.delete()
                
                request.user.foto_perfil = request.FILES['foto_perfil']
                request.user.save()
                messages.success(request, 'Foto de perfil actualizada exitosamente.')
                
            except Exception as e:
                logger.error(f'Error al actualizar foto de perfil: {str(e)}')
                messages.error(request, 'Error al actualizar la foto de perfil.')
            
            return redirect('usuarios:perfil')
        
        # Si se están actualizando otros datos del perfil
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        
        if not nombre:
            messages.error(request, 'El nombre es obligatorio.')
            return redirect('usuarios:perfil')
        
        try:
            request.user.nombre = nombre
            request.user.telefono = telefono
            request.user.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            
        except Exception as e:
            logger.error(f'Error al actualizar perfil: {str(e)}')
            messages.error(request, 'Error al actualizar el perfil.')
        
        return redirect('usuarios:perfil')
    
    return render(request, 'usuarios/perfil.html')

@login_required
def dashboard(request):
    """Vista del dashboard del usuario."""
    context = {
        'reservas_activas': Reserva.objects.filter(
            usuario=request.user,
            fecha_viaje__gte=timezone.now().date()
        ).order_by('fecha_viaje'),
        'historial_viajes': Reserva.objects.filter(
            usuario=request.user,
            fecha_viaje__lt=timezone.now().date()
        ).order_by('-fecha_viaje'),
        'now': timezone.now().date()
    }
    return render(request, 'usuarios/dashboard.html', context)

@login_required
def cancelar_reserva(request, reserva_id):
    """Vista para cancelar una reserva."""
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    
    if reserva.fecha_viaje <= timezone.now().date():
        messages.error(request, 'No se puede cancelar un viaje que ya pasó.')
        return redirect('usuarios:dashboard')
    
    try:
        reserva.delete()
        messages.success(request, 'Reserva cancelada exitosamente.')
    except Exception as e:
        logger.error(f'Error al cancelar reserva: {str(e)}')
        messages.error(request, 'Ocurrió un error al cancelar la reserva.')
    
    return redirect('usuarios:dashboard')

def recuperar_cuenta(request):
    """Vista para recuperar cuenta."""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if not email:
            messages.error(request, 'Por favor ingresa tu email.')
            return redirect('usuarios:recuperar_cuenta')
        
        try:
            usuario = Usuario.objects.get(email=email)
            
            # Generar token
            token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
            usuario.reset_token = token
            usuario.reset_token_created = timezone.now()
            usuario.save()
            
            # Enviar email
            subject = 'Recuperación de cuenta'
            html_content = render_to_string('usuarios/emails/recuperar_cuenta.html', {
                'usuario': usuario,
                'token': token,
                'domain': request.get_host(),
            })
            text_content = strip_tags(html_content)
            
            try:
                msg = EmailMultiAlternatives(
                    subject,
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                
                messages.success(
                    request,
                    'Te hemos enviado un email con instrucciones para recuperar tu cuenta.'
                )
                return redirect('usuarios:login')
                
            except SMTPException as e:
                logger.error(f'Error al enviar email de recuperación: {str(e)}')
                messages.error(
                    request,
                    'No pudimos enviar el email. Por favor, intenta más tarde.'
                )
                
        except Usuario.DoesNotExist:
            # Por seguridad, no revelamos si el email existe o no
            messages.success(
                request,
                'Si el email está registrado, recibirás instrucciones para recuperar tu cuenta.'
            )
            return redirect('usuarios:login')
            
        except Exception as e:
            logger.error(f'Error en recuperación de cuenta: {str(e)}')
            messages.error(
                request,
                'Ocurrió un error al procesar tu solicitud. Por favor, intenta más tarde.'
            )
    
    return render(request, 'usuarios/recuperar_cuenta.html')