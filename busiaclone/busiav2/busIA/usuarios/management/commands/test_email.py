from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

class Command(BaseCommand):
    help = 'Envía un correo de prueba'

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Iniciando prueba de envío de correo...'))
            
            # Preparar el mensaje
            html_message = """
            <html>
            <body>
                <h2>Prueba de Correo</h2>
                <p>Este es un correo de prueba del sistema BusIA.</p>
                <p>Si recibes este correo, significa que la configuración SMTP está funcionando correctamente.</p>
            </body>
            </html>
            """
            
            self.stdout.write(f'Usando configuración:')
            self.stdout.write(f'HOST: {settings.EMAIL_HOST}')
            self.stdout.write(f'PORT: {settings.EMAIL_PORT}')
            self.stdout.write(f'USER: {settings.EMAIL_HOST_USER}')
            self.stdout.write(f'TLS: {settings.EMAIL_USE_TLS}')
            
            # Crear el correo
            email = EmailMessage(
                subject='[BusIA] Correo de Prueba',
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['lejotape@gmail.com'],  # Cambia esto por tu correo
                reply_to=['no-reply@busia.com']
            )
            email.content_subtype = "html"
            
            # Enviar
            self.stdout.write('Enviando correo...')
            email.send(fail_silently=False)
            
            self.stdout.write(self.style.SUCCESS('¡Correo enviado exitosamente!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al enviar correo: {str(e)}'))
