from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from .models import Alumno, Asistencia
from django.utils import timezone
from datetime import datetime
import qrcode
from io import BytesIO
from django.core.files import File

def es_usuario_autorizado(user):
    return user.is_authenticated and user.is_staff

# 1. VISTA DE LOGIN
@csrf_exempt
def login_view(request):
    mensaje = ""
    tipo_alerta = ""
    
    if request.method == 'POST':
        usuario_ingresado = request.POST.get('username')
        password_ingresada = request.POST.get('password')
        
        user = authenticate(request, username=usuario_ingresado, password=password_ingresada)
        
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('/')
            else:
                mensaje = "⚠️ Esta cuenta no tiene permisos de administrador."
                tipo_alerta = "warning"
        else:
            mensaje = "❌ Usuario o contraseña incorrectos."
            tipo_alerta = "danger"

    alerta_html = f'<div class="alert alert-{tipo_alerta} text-center fw-bold rounded-4 shadow-sm">{mensaje}</div>' if mensaje else ''

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Iniciar Sesión - IPET 1308</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light d-flex align-items-center py-5" style="min-height: 100vh;">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-5">
                    <div class="card shadow-lg border-0 p-4 bg-white rounded-4">
                        <div class="text-center mb-4">
                            <h2 class="fw-bold text-primary">🏫 IPET 1308</h2>
                            <p class="text-muted">Acceso Restringido - Administradores</p>
                        </div>
                        
                        {alerta_html}

                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label fw-bold">Usuario:</label>
                                <input type="text" class="form-control form-control-lg rounded-3" name="username" required autofocus>
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-bold">Contraseña:</label>
                                <input type="password" class="form-control form-control-lg rounded-3" name="password" required>
                            </div>
                            <div class="d-grid gap-2 mt-4">
                                <button type="submit" class="btn btn-primary btn-lg fw-bold rounded-3 shadow-sm">🔑 Ingresar al Sistema</button>
                                <a href="/escaner/" class="btn btn-outline-secondary rounded-3">📷 Ir al Escáner QR</a>
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

def logout_view(request):
    logout(request)
    return redirect('/login/')

# 2. PANEL DE CONTROL EN TIEMPO REAL
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
            <td><span class="badge bg-{badge_color} px-3 py-2">{asis.estado}</span></td>
            <td>{asis.fecha_hora.strftime('%H:%M:%S')}</td>
        </tr>
        """

    if not filas_tabla:
        filas_tabla = "<tr><td colspan='4' class='text-center text-muted py-4'>No hay registros de asistencia todavía en el día de hoy.</td></tr>"

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel de Asistencias - IPET 1308</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <meta http-equiv="refresh" content="5">
    </head>
    <body class="bg-light">
        <div class="container py-5">
            <div class="d-flex justify-content-between align-items-center mb-5">
                <div>
                    <h1 class="display-5 fw-bold text-primary">🏫 IPET 1308</h1>
                    <p class="lead text-secondary mb-0">Panel de Control en Tiempo Real</p>
                </div>
                <div>
                    <a href="/logout/" class="btn btn-outline-danger fw-semibold rounded-pill px-4 shadow-sm">🚪 Cerrar Sesión</a>
                </div>
            </div>

            <div class="row text-center mb-4">
                <div class="col-md-6 mb-3">
                    <div class="card shadow-sm border-0 p-4 bg-white rounded-4">
                        <h2 class="display-4 fw-bold text-dark">{total_alumnos}</h2>
                        <p class="text-muted mb-0 fw-semibold">Alumnos Registrados</p>
                    </div>
                </div>
                <div class="col-md-6 mb-3">
                    <div class="card shadow-sm border-0 p-4 bg-white rounded-4">
                        <h2 class="display-4 fw-bold text-success">{total_presentes}</h2>
                        <p class="text-muted mb-0 fw-semibold">Registros Hoy</p>
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
                    <a href="/reporte/" class="btn btn-success btn-lg shadow-sm py-3 fw-semibold rounded-3">
                        📊 Ver Reporte Diario Completo
                    </a>
                    <a href="/alumnos/" class="btn btn-primary btn-lg shadow-sm py-3 fw-semibold rounded-3">
                        👥 Gestionar Alumnos
                    </a>
                    <a href="/alumnos/agregar/" class="btn btn-outline-primary btn-lg py-3 fw-semibold rounded-3">
                        ➕ Registrar Nuevo Alumno
                    </a>
                    <a href="/escaner/" class="btn btn-outline-info btn-lg py-3 fw-semibold rounded-3 text-dark">
                        📷 Ir al Escáner QR de Alumnos
                    </a>
                    <a href="/admin-seguro/" class="btn btn-secondary btn-sm mt-2 text-white rounded-3 py-2">
                        ⚙️ Ir al Panel de Administración Técnico (Pide Clave)
                    </a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)

# 3. ESCÁNER QR (Conectado a escaner.html)
@csrf_exempt
def escaner_view(request):
    mensaje = ""
    tipo_alerta = ""
    
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        accion = request.POST.get('accion')
            
        if codigo and codigo != "Esperando código QR..." and accion:
            codigo = codigo.strip()
            try:
                alumno = Alumno.objects.filter(codigo_identificador__iexact=codigo).first()
                if not alumno:
                    alumno = Alumno.objects.filter(dni__iexact=codigo).first()
                if not alumno:
                    alumno = Alumno.objects.filter(codigo_identificador__icontains=codigo).first()
                
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
                        if asistencia.estado == 'Retirado':
                             mensaje = f"⚠️ {alumno.nombre} {alumno.apellido} ya figuraba como retirado hoy."
                             tipo_alerta = "warning"
                        else:
                            asistencia.estado = 'Retirado'
                            asistencia.save()
                            mensaje = f"🚪 {alumno.nombre} {alumno.apellido} se ha registrado como RETIRADO."
                            tipo_alerta = "info"
                    else:
                        Asistencia.objects.create(alumno=alumno, estado='Retirado')
                        mensaje = f"🚪 Retiro registrado para {alumno.nombre} {alumno.apellido}."
                        tipo_alerta = "info"
            except Alumno.DoesNotExist:
                mensaje = f"❌ Error: El código o DNI '{codigo}' no fue encontrado en la base de datos."
                tipo_alerta = "danger"
        else:
            if not codigo or codigo == "Esperando código QR...":
                mensaje = "❌ Error: Debes escanear un código QR con la cámara primero."
            elif not accion:
                mensaje = "❌ Error: No se seleccionó ninguna acción."
            tipo_alerta = "danger"

    context = {
        'mensaje': mensaje,
        'tipo_alerta': tipo_alerta,
    }
    return render(request, 'asistencias/escaner.html', context)

# 4. REPORTE DIARIO COMPLETO (Con filtrado por fecha)
@user_passes_test(es_usuario_autorizado, login_url='/login/')
def reporte_diario_view(request):
    hoy = timezone.now().date()
    fecha_str = request.GET.get('fecha')
    
    if fecha_str:
        try:
            fecha_filtro = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha_filtro = hoy
    else:
        fecha_filtro = hoy

    asistencias = Asistencia.objects.filter(fecha_hora__date=fecha_filtro).order_by('-fecha_hora')
    
    context = {
        'fecha_filtro': fecha_filtro.strftime('%Y-%m-%d'),
        'asistencias': asistencias,
        'total_asistencias': asistencias.count(),
        'total_presentes': asistencias.filter(estado='Presente').count(),
        'total_retirados': asistencias.filter(estado='Retirado').count(),
    }
    
    return render(request, 'asistencias/reporte_diario.html', context)

# 6. GESTIONAR / LISTAR ALUMNOS (Conectado a lista_alumnos.html)
@user_passes_test(es_usuario_autorizado, login_url='/login/')
def lista_alumnos_view(request):
    alumnos = Alumno.objects.all().order_by('apellido', 'nombre')
    context = {
        'alumnos': alumnos,
    }
    return render(request, 'asistencias/lista_alumnos.html', context)

# 5. REGISTRAR NUEVO ALUMNO (Con formato estricto IPET1308-DNI en QR y archivo)
@user_passes_test(es_usuario_autorizado, login_url='/login/')
def agregar_alumno_view(request):
    mensaje = ""
    tipo_alerta = ""
    alumno_creado = None
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        dni = request.POST.get('dni')
        
        if nombre and apellido and dni:
            nombre = nombre.strip()
            apellido = apellido.strip()
            dni = dni.strip().replace('.', '')  # Limpiamos puntos si los ingresan
            try:
                codigo_generado = f"IPET1308-{dni}"
                
                # 1. Instanciamos el alumno sin guardar aún
                alumno_creado = Alumno(
                    nombre=nombre,
                    apellido=apellido,
                    dni=dni,
                    codigo_identificador=codigo_generado
                )
                
                # 2. Generamos la imagen física del QR con el código obligatorio
                img = qrcode.make(codigo_generado)
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                
                # 3. Guardamos la imagen en el ImageField con el nombre limpio IPET1308-DNI
                nombre_archivo = f"QR_{codigo_generado}.png"
                alumno_creado.qr_code.save(nombre_archivo, File(buffer), save=True)
                
                mensaje = f"✅ Alumno {apellido}, {nombre} registrado con éxito y QR generado."
                tipo_alerta = "success"
            except Exception as e:
                mensaje = f"❌ Error al registrar: Es posible que el DNI '{dni}' ya esté registrado en la base de datos."
                tipo_alerta = "danger"
        else:
            mensaje = "⚠️ Todos los campos son obligatorios."
            tipo_alerta = "warning"

    context = {
        'mensaje': mensaje,
        'tipo_alerta': tipo_alerta,
        'alumno': alumno_creado,
    }
    return render(request, 'asistencias/agregar_alumno.html', context)

@login_required
def portal_alumno(request):
    return HttpResponse("<h1>Portal del Alumno</h1><p>Vista exclusiva para alumnos.</p>")

@login_required
def admin_seguro_view(request):
    logout(request)
    return redirect('/admin/login/?next=/admin/')