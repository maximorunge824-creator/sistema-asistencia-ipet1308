"""
URL configuration for sistema_asistencia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import and include() -> path('', views.dashboard_view, name='dashboard'),
    2. Add a URL to urlpatterns | path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('asistencias.urls')),
]