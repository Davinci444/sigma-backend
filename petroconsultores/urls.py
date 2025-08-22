# Archivo: petroconsultores/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView # <-- Importamos la herramienta de redirección

urlpatterns = [
    # Nueva línea: Redirige la página de inicio a /admin/
    path('', RedirectView.as_view(url='/admin/', permanent=False)),

    path('admin/', admin.site.urls),
    path('api/', include('flota.urls')),
]