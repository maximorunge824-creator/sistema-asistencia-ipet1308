from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('escaner/', views.escaner_view, name='escaner'),
    path('reporte/', views.reporte_diario_view, name='reporte_diario'),
    path('alumnos/', views.lista_alumnos_view, name='lista_alumnos'),
    path('alumnos/agregar/', views.agregar_alumno_view, name='agregar_alumno'),
]