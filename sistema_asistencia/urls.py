"""
URL configuration for sistema_asistencia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an existing code import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('asistencias.urls')),
]

# Configuración para servir archivos multimedia (QR codes) en modo desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)