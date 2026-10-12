from django.db import models

class Alumno(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    codigo_identificador = models.CharField(max_length=100, unique=True, blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

class Asistencia(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50, default='Presente')

    def __str__(self):
        return f"{self.alumno} - {self.fecha_hora} ({self.estado})"

class HorarioEscolar(models.Model):
    dia_semana = models.CharField(max_length=20, choices=[
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
    ])
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()

    def __str__(self):
        return f"{self.dia_semana}: {self.hora_entrada} a {self.hora_salida}"

class CalendarioEscolar(models.Model):
    fecha = models.DateField(unique=True)
    descripcion = models.CharField(max_length=255)
    es_habil = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.fecha}: {self.descripcion}"