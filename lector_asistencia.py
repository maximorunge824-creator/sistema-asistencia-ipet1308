import os
import django
from datetime import datetime
import cv2
from pyzbar.pyzbar import decode
from django.utils import timezone

# 1. Configurar el entorno de Django para usar los modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_asistencia.settings')
django.setup()

from asistencias.models import Alumno, Asistencia, HorarioEscolar, CalendarioEscolar

def registrar_ingreso_alumno(codigo_qr):
    try:
        alumno = Alumno.objects.get(codigo_identificador=codigo_qr)
    except Alumno.DoesNotExist:
        print(f"[ERROR] Código QR no reconocido en el sistema: {codigo_qr}")
        return

    hoy = timezone.localdate()
    ahora = timezone.localtime()

    # ==========================================
    # 2. VERIFICACIÓN ESTRICTA (¡Anti-duplicados!)
    # ==========================================
    asistencia_existente = Asistencia.objects.filter(
        alumno=alumno, 
        fecha_hora__date=hoy
    ).first()

    if asistencia_existente:
        print(f"[AVISO] {alumno.nombre} {alumno.apellido} ya registró su asistencia hoy a las {asistencia_existente.fecha_hora.strftime('%H:%M:%S')}. Estado: {asistencia_existente.estado}")
        return  # Se frena acá para no crear otro registro en el día.

    # ==========================================
    # 3. LÓGICA DE HORARIOS Y TOLERANCIA
    # ==========================================
    horario = HorarioEscolar.objects.first()
    
    if horario:
        hora_actual = ahora.time()
        minutos_actual = hora_actual.hour * 60 + hora_actual.minute
        minutos_entrada = horario.hora_entrada.hour * 60 + horario.hora_entrada.minute
        dif = minutos_actual - minutos_entrada

        if dif <= horario.minutos_tolerancia_tarde:
            estado = 'Presente'
        elif dif <= horario.minutos_limite_tarde:
            estado = 'Tarde'
        else:
            estado = 'Ausente'
    else:
        estado = 'Presente'

    # 4. Guardar por única vez en el día
    Asistencia.objects.create(
        alumno=alumno,
        fecha_hora=ahora,
        estado=estado
    )
    print(f"[ÉXITO] Asistencia registrada para {alumno.apellido}, {alumno.nombre} - Estado: {estado}")

def iniciar_escaner():
    cap = cv2.VideoCapture(0)
    print("Iniciando escáner QR para IPET 1308... Presioná 'q' para salir.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        for barcode in decode(frame):
            codigo_qr = barcode.data.decode('utf-8')
            registrar_ingreso_alumno(codigo_qr)
            # Pausa para evitar lecturas consecutivas rápidas del mismo fotograma
            cv2.waitKey(2000) 

        cv2.imshow('Lector de Asistencia - IPET 1308', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    iniciar_escaner()