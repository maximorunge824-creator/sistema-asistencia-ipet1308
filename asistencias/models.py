from django.db import models

class Alumno(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    codigo_identificador = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.codigo_identificador})"

class HorarioEscolar(models.Model):
    descripcion = models.CharField(max_length=50, default="Turno Mañana")
    hora_entrada = models.TimeField()
    minutos_tolerancia_tarde = models.IntegerField(default=10, help_text="Minutos hasta los cuales se considera Presente")
    minutos_limite_tarde = models.IntegerField(default=30, help_text="Minutos hasta los cuales se considera Tarde (luego pasa a Ausente)")

    def __str__(self):
        return f"{self.descripcion} - Ingreso: {self.hora_entrada.strftime('%H:%M')}"

class CalendarioEscolar(models.Model):
    TIPO_DIA = [
        ('Clases', 'Día de Clases'),
        ('Feriado', 'Feriado / Asueto'),
        ('Receso', 'Receso Escolar / Vacaciones'),
    ]
    
    fecha = models.DateField(unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_DIA, default='Clases')
    descripcion = models.CharField(max_length=100, blank=True, null=True, help_text="Ej: Feriado Nacional, Día del Estudiante, etc.")

    def __str__(self):
        return f"{self.fecha.strftime('%d/%m/%Y')} - {self.get_tipo_display()} ({self.descripcion or 'Sin detalle'})"

class Asistencia(models.Model):
    ESTADOS = [
        ('Presente', 'Presente'),
        ('Tarde', 'Tarde'),
        ('Ausente', 'Ausente'),
    ]
    
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Presente')

    def __str__(self):
        return f"{self.alumno} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')} [{self.estado}]"