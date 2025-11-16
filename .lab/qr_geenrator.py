import qrcode
from PIL import Image

# Datos que quieres codificar en el QR
datos = "https://github.com/qnowtech/Quantum-Network-Knowledge-Graph"

# Crear una instancia de QRCode
qr = qrcode.QRCode(
    version=1,  # Controla el tamaño del QR (1-40)
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # Nivel de corrección de errores
    box_size=10,  # Tamaño de cada "caja" del QR
    border=4,  # Grosor del borde (mínimo 4)
)

# Agregar datos al QR
qr.add_data(datos)
qr.make(fit=True)

# Crear la imagen del QR
img = qr.make_image(fill_color="black", back_color="white")

# Guardar la imagen
img.save("codigo_qr.png")

print("✓ Código QR generado exitosamente: codigo_qr.png")

# --- Versión más simple (una sola línea) ---
img = qrcode.make("https://github.com/qnowtech/Quantum-Network-Knowledge-Graph")
img.save("qr_simple.png")