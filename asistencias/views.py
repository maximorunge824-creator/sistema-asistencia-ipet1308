from django.shortcuts import redirect
from django.http import HttpResponse
from .models import Alumno, Asistencia
from django.utils import timezone

def dashboard_view(request):
    total_alumnos = Alumno.objects.count()
    asistencias_hoy = Asistencia.objects.filter(fecha_hora__date=timezone.now().date()).count()
    
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel de Asistencias - IPET 1308</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container py-5">
            <div class="text-center mb-5">
                <h1 class="display-5 fw-bold text-primary">🏫 IPET 1308</h1>
                <p class="lead text-secondary">Sistema Moderno de Control de Asistencias</p>
            </div>

            <div class="row text-center mb-5">
                <div class="col-md-6 mb-3">
                    <div class="card shadow-sm border-0 p-4 bg-white rounded-4">
                        <h2 class="display-4 fw-bold text-dark">{total_alumnos}</h2>
                        <p class="text-muted mb-0">Alumnos Registrados</p>
                    </div>
                </div>
                <div class="col-md-6 mb-3">
                    <div class="card shadow-sm border-0 p-4 bg-white rounded-4">
                        <h2 class="display-4 fw-bold text-success">{asistencias_hoy}</h2>
                        <p class="text-muted mb-0">Presentes Hoy</p>
                    </div>
                </div>
            </div>

            <div class="row justify-content-center">
                <div class="col-md-6 d-grid gap-3">
                    <a href="/escaner/" class="btn btn-warning btn-lg shadow-sm py-3 fw-bold text-dark">
                        📷 Pantalla de Escaneo (Ingreso / Retiro)
                    </a>
                    <a href="/reporte/" class="btn btn-success btn-lg shadow-sm py-3 fw-semibold">
                        📊 Ver Reporte Diario
                    </a>
                    <a href="/alumnos/" class="btn btn-primary btn-lg shadow-sm py-3 fw-semibold">
                        👥 Gestionar Alumnos
                    </a>
                    <a href="/alumnos/agregar/" class="btn btn-outline-primary btn-lg py-3 fw-semibold">
                        ➕ Registrar Nuevo Alumno
                    </a>
                    <a href="/admin/" class="btn btn-secondary btn-sm mt-4 text-white">
                        ⚙️ Ir al Panel de Administración Técnico
                    </a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)

def escaner_view(request):
    mensaje = ""
    tipo_alerta = ""
    
    if request.method == 'POST':
        codigo = request.POST.get('codigo_identificador')
        accion = request.POST.get('accion') # 'ingreso' o 'retiro'
        
        try:
            alumno = Alumno.objects.get(codigo_identificador=codigo)
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
            mensaje = "❌ Error: Código de alumno no encontrado en el sistema."
            tipo_alerta = "danger"

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Escaneo de Asistencia - IPET 1308</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    </head>
    <body class="bg-light">
        <div class="container py-4">
            <div class="text-center mb-3">
                <h1 class="fw-bold text-primary">📷 Terminal de Escaneo IPET 1308</h1>
                <p class="text-muted">Use la cámara o ingrese el código del alumno</p>
            </div>

            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card shadow border-0 p-4 bg-white rounded-4">
                        
                        <div class="text-center mb-3">
                            <button type="button" id="btn-activar-camara" class="btn btn-outline-primary fw-bold w-100 py-2" onclick="toggleCamara()">
                                📹 Activar Cámara para Escanear
                            </button>
                        </div>

                        <div id="reader" style="width: 100%; display: none;" class="mb-3 rounded overflow-hidden"></div>

                        <form method="POST" id="form-asistencia">
                            <div class="mb-3">
                                <label for="codigo_identificador" class="form-label fw-bold">Código Identificador:</label>
                                <input type="text" name="codigo_identificador" id="codigo_identificador" class="form-control form-control-lg text-center" placeholder="Escanee o escriba el código..." autofocus required>
                            </div>
                            
                            <div class="d-grid gap-2 mb-3">
                                <button type="submit" name="accion" value="ingreso" class="btn btn-success btn-lg fw-bold">
                                    📥 Registrar Ingreso (Presente)
                                </button>
                                <button type="submit" name="accion" value="retiro" class="btn btn-danger btn-lg fw-bold">
                                    🚪 Registrar Retiro Anticipado
                                </button>
                            </div>
                        </form>

                        {f'<div class="alert alert-{tipo_alerta} text-center fw-bold mt-3" role="alert">{mensaje}</div>' if mensaje else ''}
                        
                        <div class="text-center mt-3">
                            <a href="/" class="btn btn-outline-secondary btn-sm">← Volver al Panel Principal</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let html5QrCode;
            let camaraActiva = false;

            function toggleCamara() {{
                const readerDiv = document.getElementById('reader');
                const btnCamara = document.getElementById('btn-activar-camara');
                const inputCodigo = document.getElementById('codigo_identificador');

                if (!camaraActiva) {{
                    readerDiv.style.display = 'block';
                    btnCamara.textContent = '❌ Apagar Cámara';
                    btnCamara.classList.replace('btn-outline-primary', 'btn-outline-danger');
                    
                    html5QrCode = new Html5Qrcode("reader");
                    html5QrCode.start(
                        {{ facingMode: "environment" }},
                        {{ fps: 10, qrbox: {{ width: 250, height: 150 }} }},
                        (decodedText, decodedResult) => {{
                            inputCodigo.value = decodedText;
                            toggleCamara();
                        }},
                        (errorMessage) => {{}}
                    ).catch((err) => {{
                        alert("No se pudo acceder a la cámara: " + err);
                        toggleCamara();
                    }});
                    camaraActiva = true;
                }} else {{
                    if (html5QrCode) {{
                        html5QrCode.stop().then(() => {{
                            readerDiv.style.display = 'none';
                            btnCamara.textContent = '📹 Activar Cámara para Escanear';
                            btnCamara.classList.replace('btn-outline-danger', 'btn-outline-primary');
                            camaraActiva = false;
                        }}).catch((err) => {{
                            console.log("Error al detener la cámara", err);
                        }});
                    }}
                }}
            }}
        </script>
    </body>
    </html>
    """
    return HttpResponse(html)

def reporte_diario_view(request):
    return HttpResponse("<h1>Reporte Diario</h1><a href='/'>Volver al inicio</a>")

def lista_alumnos_view(request):
    return HttpResponse("<h1>Lista de Alumnos</h1><a href='/'>Volver al inicio</a>")

def agregar_alumno_view(request):
    return HttpResponse("<h1>Agregar Alumno</h1><a href='/'>Volver al inicio</a>")