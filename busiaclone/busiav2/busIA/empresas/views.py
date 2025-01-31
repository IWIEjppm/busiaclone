from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def login_empresa(request):
    return render(request, 'empresas/loginempresa.html')