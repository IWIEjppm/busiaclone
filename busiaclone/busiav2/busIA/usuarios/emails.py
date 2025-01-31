"""
Módulo para manejar el envío de emails en la aplicación de usuarios.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def enviar_codigo_verificacion(usuario):
    """
    Envía el código de verificación al email del usuario.
    """
    asunto = 'Verifica tu cuenta'
    html_mensaje = render_to_string('usuarios/emails/verificacion.html', {
        'usuario': usuario,
        'codigo': usuario.codigo_verificacion
    })
    mensaje_plano = strip_tags(html_mensaje)
    
    return send_mail(
        asunto,
        mensaje_plano,
        settings.DEFAULT_FROM_EMAIL,
        [usuario.email],
        html_message=html_mensaje,
        fail_silently=False
    )

def enviar_codigo_recuperacion(usuario, email_destino):
    """
    Envía el código de recuperación al email especificado.
    """
    asunto = 'Recuperación de cuenta'
    html_mensaje = render_to_string('usuarios/emails/recuperacion.html', {
        'usuario': usuario,
        'codigo': usuario.codigo_recuperacion
    })
    mensaje_plano = strip_tags(html_mensaje)
    
    return send_mail(
        asunto,
        mensaje_plano,
        settings.DEFAULT_FROM_EMAIL,
        [email_destino],
        html_message=html_mensaje,
        fail_silently=False
    )
