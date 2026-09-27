import os
import django
from datetime import datetime, date

# Configuración del entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_asistencia.settings')
django.setup()

from asistencias.models import Alumno, Asistencia, CalendarioEscolar

def generar_reporte_fecha(fecha_consulta):
    print(f"\n==================================================")
    print(f" REPORTE DE ASISTENCIA - IPET 1308")
    print(f" Fecha: {fecha_consulta.strftime('%d/%m/%Y')}")
    print(f"==================================================")

    # 1. Verificar si el día tuvo clases según el calendario
    calendario = CalendarioEscolar.objects.filter(fecha=fecha_consulta).first()
    if calendario and calendario.tipo != 'Clases':
        print(f"[AVISO] Este día figura en el calendario como: {calendario.get_tipo_display()} ({calendario.descripcion or 'Sin actividad'}).")
        print("No se computan asistencias ni inasistencias.")
        return

    # 2. Obtener todos los alumnos registrados en el sistema
    todos_los_alumnos = Alumno.objects.all()
    total_alumnos = todos_los_alumnos.count()

    if total_alumnos == 0:
        print("[ALERTA] No hay alumnos cargados en el sistema.")
        return

    # 3. Obtener las asistencias registradas en esa fecha específica
    asistencias_dia = Asistencia.objects.filter(fecha_hora__date=fecha_consulta)
    
    # Mapear las asistencias por ID de alumno para búsqueda rápida
    mapa_asistencias = {asist.alumno_id: asist for asist in asistencias_dia}

    presentes = []
    tardes = []
    ausentes = []

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
            # Si no marcó entrada y el día era de clases, cuenta como Ausente
            ausentes.append(alumno)

    # 4. Mostrar Estadísticas Resumidas
    print(f"\n--- ESTADÍSTICAS GENERALES ---")
    print(f"Total de Alumnos Matrículados: {total_alumnos}")
    print(f"🟢 Presentes: {len(presentes)}")
    print(f"🟡 Tarde:     {len(tardes)}")
    print(f"🔴 Ausentes:  {len(ausentes)}")
    
    # Calcular porcentaje de asistencia (Presentes + Tarde) sobre el total
    asistieron_count = len(presentes) + len(tardes)
    porcentaje = (asistieron_count / total_alumnos) * 100 if total_alumnos > 0 else 0
    print(f"📊 Porcentaje de Asistencia General: {porcentaje:.1f}%\n")

    # 5. Listados detallados
    if presentes:
        print("--- ALUMNOS PRESENTES (A tiempo) ---")
        for alum, hora in presentes:
            print(f"  • {alum.apellido}, {alum.nombre} ({alum.codigo_identificador}) - Ingreso: {hora.strftime('%H:%M:%S')}")

    if tardes:
        print("\n--- ALUMNOS CON LLEGADA TARDE ---")
        for alum, hora in tardes:
            print(f"  • {alum.apellido}, {alum.nombre} ({alum.codigo_identificador}) - Ingreso: {hora.strftime('%H:%M:%S')}")

    if ausentes:
        print("\n--- ALUMNOS AUSENTES ---")
        for alum in ausentes:
            print(f"  • {alum.apellido}, {alum.nombre} ({alum.codigo_identificador})")
            
    print("==================================================\n")

if __name__ == '__main__':
    while True:
        print("¿Qué reporte deseas generar?")
        print("1. Ver el reporte de HOY")
        print("2. Ver el reporte de otra fecha (Formato: DD/MM/AAAA)")
        print("3. Salir")
        
        opcion = input("Ingresá una opción (1, 2 o 3): ").strip()
        
        if opcion == '1':
            generar_reporte_fecha(date.today())
        elif opcion == '2':
            fecha_str = input("Ingresá la fecha (ej: 25/09/2026): ").strip()
            try:
                fecha_ingresada = datetime.strptime(fecha_str, '%d/%m/%Y').date()
                generar_reporte_fecha(fecha_ingresada)
            except ValueError:
                print("[ERROR] Formato de fecha incorrecto. Usá el formato DD/MM/AAAA.")
        elif opcion == '3':
            print("Saliendo del generador de reportes...")
            break
        else:
            print("[OPCIÓN INVÁLIDA] Por favor, elegí 1, 2 o 3.")