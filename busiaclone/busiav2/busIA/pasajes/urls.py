from django.urls import path
from . import views

app_name = 'pasajes'

urlpatterns = [
    # Páginas
    path('', views.index, name='index'),
    path('comprar/', views.comprar, name='comprar'),
    path('mis-viajes/', views.mis_viajes, name='mis_viajes'),
    
    # APIs de búsqueda
    path('api/ciudades/buscar/', views.buscar_ciudades, name='buscar_ciudades'),
    path('api/viajes/buscar/', views.buscar_viajes_api, name='buscar_viajes'),
    
    # APIs de reserva
    path('api/asientos/<int:viaje_id>/', views.obtener_asientos_api, name='obtener_asientos'),
    path('api/reservas/crear/', views.crear_reserva, name='crear_reserva'),
    path('api/reservas/<int:reserva_id>/confirmar/', views.confirmar_pago, name='confirmar_pago'),
]
