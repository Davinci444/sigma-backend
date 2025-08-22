# Archivo: petroconsultores/urls.py

from django.contrib import admin
from django.urls import path, include # <-- Asegúrate de que 'include' esté aquí

urlpatterns = [
    path('admin/', admin.site.urls),
    # Nueva línea: cualquier dirección que empiece con 'api/' será manejada por nuestra app 'flota'.
    path('api/', include('flota.urls')),
]