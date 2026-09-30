from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'), # Panel de administración (pide clave)
    path('login/', LoginView.as_view(template_name='asistencias/login.html', next_page='/'), name='login'),
    path('escaner/', views.escaner_view, name='escaner'), # Pantalla libre para los estudiantes
    path('reporte/', views.reporte_diario_view, name='reporte_diario'),
    path('alumnos/', views.lista_alumnos_view, name='lista_alumnos'),
    path('alumnos/agregar/', views.agregar_alumno_view, name='agregar_alumno'),
    path('portal/', views.portal_alumno, name='portal_alumno'),
]