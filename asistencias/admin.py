from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from datetime import datetime, date
from .models import Alumno, HorarioEscolar, CalendarioEscolar, Asistencia

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'codigo_identificador')
    search_fields = ('apellido', 'nombre', 'codigo_identificador')

@admin.register(HorarioEscolar)
class HorarioEscolarAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'hora_entrada', 'minutos_tolerancia_tarde', 'minutos_limite_tarde')

@admin.register(CalendarioEscolar)
class CalendarioEscolarAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tipo', 'descripcion')
    list_filter = ('tipo', 'fecha')
    search_fields = ('descripcion', 'fecha')

@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('alumno', 'fecha_hora', 'estado')
    list_filter = ('estado', 'fecha_hora')
    date_hierarchy = 'fecha_hora'
    search_fields = ('alumno__nombre', 'alumno__apellido', 'alumno__codigo_identificador')

    # Añadir URL personalizada para el reporte visual
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('reporte-visual/', self.admin_site.admin_view(self.reporte_visual_view), name='asistencias_reporte_visual'),
        ]
        return custom_urls + urls

    def reporte_visual_view(self, request):
        hoy = date.today()
        fecha_str = request.GET.get('fecha')
        
        if fecha_str:
            try:
                fecha_consulta = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                fecha_consulta = hoy
        else:
            fecha_consulta = hoy

        calendario = CalendarioEscolar.objects.filter(fecha=fecha_consulta).first()
        es_clases = True
        mensaje_calendario = ""
        if calendario and calendario.tipo != 'Clases':
            es_clases = False
            mensaje_calendario = f"Atención: Este día figura en el calendario como {calendario.get_tipo_display()} ({calendario.descripcion or 'Sin actividad'})."

        todos_los_alumnos = Alumno.objects.all()
        total_alumnos = todos_los_alumnos.count()
        
        asistencias_dia = Asistencia.objects.filter(fecha_hora__date=fecha_consulta)
        mapa_asistencias = {asist.alumno_id: asist for asist in asistencias_dia}

        presentes = []
        tardes = []
        ausentes = []

        if es_clases:
            for alumno in todos_los_alumnos:
                if alumno.id in mapa_asistencias:
                    asist = mapa_asistencias[alumno.id]
                    if asist.estado == 'Presente':
                        presentes.append((alumno, asist.fecha_hora))
                    elif asist.estado == 'Tarde':
                        tardes.append((alumno, asist.fecha_hora))
                    elif asist.estado == 'Ausente':
                        ausentes.append(alumno)
                else:
                    ausentes.append(alumno)

        asistieron_count = len(presentes) + len(tardes)
        porcentaje = (asistieron_count / total_alumnos) * 100 if total_alumnos > 0 else 0

        context = dict(
            self.admin_site.each_context(request),
            fecha_consulta=fecha_consulta,
            fecha_str=fecha_consulta.strftime('%Y-%m-%d'),
            total_alumnos=total_alumnos,
            presentes=presentes,
            tardes=tardes,
            ausentes=ausentes,
            porcentaje=round(porcentaje, 1),
            es_clases=es_clases,
            mensaje_calendario=mensaje_calendario,
            opts=self.model._meta,
        )
        return TemplateResponse(request, "admin/asistencias/reporte_visual.html", context)