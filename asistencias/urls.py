from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('escaner/', views.escaner_view, name='escaner'),
    path('reporte/', views.reporte_diario_view, name='reporte'),
    path('alumnos/', views.lista_alumnos_view, name='lista_alumnos'),
    path('alumnos/agregar/', views.agregar_alumno_view, name='agregar_alumno'),
    path('portal/', views.portal_alumno, name='portal_alumno'),
    path('admin-seguro/', views.admin_seguro_view, name='admin_seguro'),
]