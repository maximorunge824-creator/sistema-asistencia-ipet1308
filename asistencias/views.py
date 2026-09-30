from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from .models import Alumno, Asistencia
from django.utils import timezone

def es_usuario_autorizado(user):
    return user.is_authenticated and user.is_staff

# 1. PANEL DE CONTROL EN TIEMPO REAL (Solo administradores)
@user_passes_test(es_usuario_autorizado, login_url='/login/')
def dashboard_view(request):
    total_alumnos = Alumno.objects.count()
    hoy = timezone.now().date()
    asistencias_hoy = Asistencia.objects.filter(fecha_hora__date=hoy).order_by('-fecha_hora')
    total_presentes = asistencias_hoy.count()
    
    filas_tabla = ""
    for asis in asistencias_hoy:
        badge_color = "success" if asis.estado == 'Presente' else "warning text-dark"
        filas_tabla += f"""
        <tr>
            <td class="fw-bold">{asis.alumno.apellido}, {asis.alumno.nombre}</td>
            <td><code>{asis.alumno.codigo_identificador}</code></td>
            <td><span class="badge bg-{badge_color}">{asis.estado}</span></td>
            <td>{asis.fecha_hora.strftime('%H:%M:%S')}</td>
        </tr>
        """

    if not filas_tabla:
        filas_tabla = "<tr><td colspan='4' class='text-center text-muted'>No hay registros de asistencia todavía en el día de hoy.</td></tr>"

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel de Asistencias - IPET 1308</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <meta http-equiv="refresh" content="10">
    </head>
    <body class="bg-light">
        <div class="container py-5">
            <div class="text-center mb-5">
                <h1 class="display-5 fw-bold text-primary">🏫 IPET 1308</h1>
                <p class="lead text-secondary">Panel de Control en Tiempo Real</p>
            </div>

            <div class="row text-center mb-4">
                <div class="col-md-6 mb-3">
                    <div class="card shadow-sm border-0 p-4 bg-white rounded-4">
                        <h2 class="display-4 fw-bold text-dark">{total_alumnos}</h2>
                        <p class="text-muted mb-0">Alumnos Registrados</p>
                    </div>
                </div>
                <div class="col-md-6 mb-3">
                    <div class="card shadow-sm border-0 p-4 bg-white rounded-4">
                        <h2 class="display-4 fw-bold text-success">{total_presentes}</h2>
                        <p class="text-muted mb-0">Registros Hoy</p>
                    </div>
                </div>
            </div>

            <div class="card shadow-sm border-0 p-4 bg-white rounded-4 mb-4">
                <h3 class="fw-bold text-secondary mb-3">📋 Últimos Registros de Hoy</h3>
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-dark">
                            <tr>
                                <th>Alumno</th>
                                <th>Código / DNI</th>
                                <th>Estado</th>
                                <th>Hora</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filas_tabla}
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="row justify-content-center">
                <div class="col-md-6 d-grid gap-3">
                    <a href="/reporte/" class="btn btn-success btn-lg shadow-sm py-3 fw-semibold">
                        📊 Ver Reporte Diario Completo
                    </a>
                    <a href="/alumnos/" class="btn btn-primary btn-lg shadow-sm py-3 fw-semibold">
                        👥 Gestionar Alumnos
                    </a>
                    <a href="/alumnos/agregar/" class="btn btn-outline-primary btn-lg py-3 fw-semibold">
                        ➕ Registrar Nuevo Alumno
                    </a>
                    <a href="/admin/" class="btn btn-secondary btn-sm mt-2 text-white">
                        ⚙️ Ir al Panel de Administración Técnico
                    </a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)

# 2. ESCÁNER (Libre para estudiantes y exento de CSRF para que el lector QR funcione)
@csrf_exempt
def escaner_view(request):
    mensaje = ""
    tipo_alerta = ""
    
    if request.method == 'POST':
        codigo = request.POST.get('codigo_identificador') or request.POST.get('codigo') or request.POST.get('dni')
        accion = request.POST.get('accion', 'ingreso')
        if not accion:
            accion = 'ingreso'
            
        if codigo:
            codigo = codigo.strip()
            
            try:
                alumno = Alumno.objects.filter(codigo_identificador=codigo).first()
                if not alumno:
                    alumno = Alumno.objects.filter(dni=codigo).first()
                    
                if not alumno:
                    raise Alumno.DoesNotExist()
                    
                hoy = timezone.now().date()
                
                if accion == 'ingreso':
                    asistencia_existente = Asistencia.objects.filter(alumno=alumno, fecha_hora__date=hoy).first()
                    if asistencia_existente:
                        mensaje = f"⚠️ {alumno.nombre} {alumno.apellido} ya tenía su ingreso registrado hoy."
                        tipo_alerta = "warning"
                    else:
                        Asistencia.objects.create(alumno=alumno, estado='Presente')
                        mensaje = f"✅ ¡Ingreso registrado con éxito para {alumno.nombre} {alumno.apellido}!"
                        tipo_alerta = "success"
                        
                elif accion == 'retiro':
                    asistencia = Asistencia.objects.filter(alumno=alumno, fecha_hora__date=hoy).first()
                    if asistencia:
                        asistencia.estado = 'Retirado'
                        asistencia.save()
                        mensaje = f"🚪 {alumno.nombre} {alumno.apellido} se ha registrado como RETIRADO."
                        tipo_alerta = "info"
                    else:
                        Asistencia.objects.create(alumno=alumno, estado='Retirado')
                        mensaje = f"🚪 Retiro registrado para {alumno.nombre} {alumno.apellido}."
                        tipo_alerta = "info"
                        
            except Alumno.DoesNotExist:
                mensaje = f"❌ Error: El código '{codigo}' no fue encontrado en el sistema."
                tipo_alerta = "danger"
        else:
            mensaje = "❌ Error: No se detectó ningún código válido."
            tipo_alerta = "danger"

    return render(request, 'asistencias/escaner.html', {
        'mensaje': mensaje,
        'tipo_alerta': tipo_alerta
    })

@user_passes_test(es_usuario_autorizado, login_url='/login/')
def reporte_diario_view(request):
    return HttpResponse("<h1>Reporte Diario</h1><a href='/'>Volver al inicio</a>")

@user_passes_test(es_usuario_autorizado, login_url='/login/')
def lista_alumnos_view(request):
    return HttpResponse("<h1>Lista de Alumnos</h1><a href='/'>Volver al inicio</a>")

@user_passes_test(es_usuario_autorizado, login_url='/login/')
def agregar_alumno_view(request):
    mensaje = ""
    tipo_alerta = ""
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        dni = request.POST.get('dni')
        
        if nombre and apellido and dni:
            try:
                codigo_generado = f"IPET1308-{dni}"
                Alumno.objects.create(
                    nombre=nombre,
                    apellido=apellido,
                    dni=dni,
                    codigo_identificador=codigo_generado
                )
                mensaje = f"✅ Alumno {apellido}, {nombre} registrado con éxito con el código {codigo_generado}"
                tipo_alerta = "success"
            except Exception as e:
                mensaje = f"❌ Error al registrar (es posible que el DNI ya exista): {e}"
                tipo_alerta = "danger"
        else:
            mensaje = "⚠️ Todos los campos son obligatorios."
            tipo_alerta = "warning"

    alerta_html = f'<div class="alert alert-{tipo_alerta} text-center fw-bold">{mensaje}</div>' if mensaje else ''

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Registrar Alumno - IPET 1308</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card shadow border-0 p-4 bg-white rounded-4">
                        <h2 class="fw-bold text-primary mb-3 text-center">➕ Nuevo Alumno</h2>
                        <p class="text-muted text-center mb-4">El código y el QR se generarán como <b>IPET1308-[DNI]</b></p>
                        
                        {alerta_html}

                        <form method="POST">
                            {{% csrf_token %}}
                            <div class="mb-3">
                                <label class="form-label fw-bold">Nombre:</label>
                                <input type="text" class="form-control" name="nombre" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-bold">Apellido:</label>
                                <input type="text" class="form-control" name="apellido" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-bold">DNI:</label>
                                <input type="text" class="form-control" name="dni" placeholder="Ej: 45123456" required>
                            </div>

                            <div class="d-grid gap-2 mt-4">
                                <button type="submit" class="btn btn-primary btn-lg fw-bold">💾 Guardar y Generar QR</button>
                                <a href="/" class="btn btn-outline-secondary">← Volver al Panel</a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)

@login_required
def portal_alumno(request):
    return HttpResponse("<h1>Portal del Alumno</h1><p>Vista exclusiva para alumnos.</p>")