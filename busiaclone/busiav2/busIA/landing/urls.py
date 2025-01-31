from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.index, name='index'),  # Página principal de la landingpage
]