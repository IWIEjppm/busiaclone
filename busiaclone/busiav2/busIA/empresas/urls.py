from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login_empresa, name='login_empresa'),
]