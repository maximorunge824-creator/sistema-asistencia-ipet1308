import qrcode

# Datos del alumno (el código tiene que coincidir con el 'codigo_identificador' que cargaste en el admin de Django)
dni_alumno = "45123456"
nombre_completo = "Rosbelque, Samuel"

# Texto que contendrá el QR
codigo_qr_texto = "IPET1308-45123456"

# Generar la imagen del código QR
img = qrcode.make(codigo_qr_texto)

# Guardar la imagen en un archivo PNG en esta misma carpeta
nombre_archivo = f"carnet_{dni_alumno}.png"
img.save(nombre_archivo)

print(f"¡Código QR generado con éxito como '{nombre_archivo}'!")
