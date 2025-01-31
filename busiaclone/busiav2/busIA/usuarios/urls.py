from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
    path('recuperar-cuenta/', views.recuperar_cuenta, name='recuperar_cuenta'),
    
    # Verificación de email
    path('verificar-email/', views.verificar_email, name='verificar_email'),
    path('reenviar-codigo/', views.reenviar_codigo, name='reenviar_codigo'),
    
    # Dashboard y perfil
    path('dashboard/', views.dashboard, name='dashboard'),
    path('perfil/', views.perfil_view, name='perfil'),
    
    # Reservas
    path('cancelar-reserva/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
]