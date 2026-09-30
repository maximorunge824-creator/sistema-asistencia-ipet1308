from django.contrib import admin
from django.utils.html import format_html
from .models import Alumno, Asistencia, HorarioEscolar, CalendarioEscolar

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'dni', 'codigo_identificador', 'ver_qr')
    search_fields = ('nombre', 'apellido', 'dni', 'codigo_identificador')

    def ver_qr(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="50" height="50" />', obj.qr_code.url)
        return "Sin QR"
    ver_qr.short_description = 'Código QR'

@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('alumno', 'estado', 'fecha_hora')
    list_filter = ('estado', 'fecha_hora')
    search_fields = ('alumno__nombre', 'alumno__apellido', 'alumno__dni', 'alumno__codigo_identificador')

@admin.register(HorarioEscolar)
class HorarioEscolarAdmin(admin.ModelAdmin):
    list_display = ('dia_semana', 'hora_entrada', 'hora_salida')

@admin.register(CalendarioEscolar)
class CalendarioEscolarAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'descripcion', 'es_habil')
    list_filter = ('es_habil',)