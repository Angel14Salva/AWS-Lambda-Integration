import json
import urllib.parse
from twilio.twiml.messaging_response import MessagingResponse

CATALOGO = {
    "polo": {"nombre": "Polo básico", "precio": 35, "stock": True, "tallas": ["S", "M", "L", "XL"]},
    "jean": {"nombre": "Jean slim fit", "precio": 89, "stock": True, "tallas": ["28", "30", "32", "34"]},
    "vestido": {"nombre": "Vestido casual", "precio": 75, "stock": True, "tallas": ["S", "M", "L"]},
    "blusa": {"nombre": "Blusa floral", "precio": 45, "stock": False, "tallas": ["S", "M"]},
    "short": {"nombre": "Short deportivo", "precio": 39, "stock": True, "tallas": ["S", "M", "L", "XL"]},
}

PEDIDOS = []

def obtener_menu():
    return (
        "👗 *Bienvenido a Moda Trujillo*\n\n"
        "¿En qué te puedo ayudar?\n\n"
        "1️⃣ Ver catálogo\n"
        "2️⃣ Precio de un producto\n"
        "3️⃣ Hacer un pedido\n"
        "4️⃣ Ver mis pedidos\n\n"
        "Escribe el número de la opción 👆"
    )

def obtener_catalogo():
    texto = "👗 *Nuestro catálogo:*\n\n"
    for clave, item in CATALOGO.items():
        estado = "✅ Disponible" if item["stock"] else "❌ Agotado"
        texto += f"• *{item['nombre']}* — S/ {item['precio']} {estado}\n"
    texto += "\nEscribe *2* para consultar precio de un producto o *3* para pedir."
    return texto

def consultar_precio(mensaje):
    mensaje_lower = mensaje.lower()
    for clave, item in CATALOGO.items():
        if clave in mensaje_lower or item["nombre"].lower() in mensaje_lower:
            tallas = ", ".join(item["tallas"])
            estado = "✅ En stock" if item["stock"] else "❌ Agotado"
            return (
                f"*{item['nombre']}*\n"
                f"💰 Precio: S/ {item['precio']}\n"
                f"📦 {estado}\n"
                f"📏 Tallas: {tallas}\n\n"
                "¿Deseas pedirlo? Escribe *3* para hacer tu pedido."
            )
    return (
        "No encontré ese producto. 😅\n\n"
        "Productos disponibles: " + ", ".join(CATALOGO.keys()) + "\n\n"
        "Escribe el nombre del producto que buscas."
    )

def iniciar_pedido(mensaje, numero_cliente):
    mensaje_lower = mensaje.lower()
    producto_encontrado = None

    for clave, item in CATALOGO.items():
        if clave in mensaje_lower or item["nombre"].lower() in mensaje_lower:
            producto_encontrado = (clave, item)
            break

    if not producto_encontrado:
        return (
            "Para hacer un pedido, dime qué producto quieres. 🛍️\n\n"
            "Ejemplo: *quiero un polo* o *pedir jean*\n\n"
            "O escribe *1* para ver el catálogo completo."
        )

    clave, item = producto_encontrado

    if not item["stock"]:
        return (
            f"Lo sentimos, *{item['nombre']}* está agotado por el momento. 😔\n\n"
            "Escribe *1* para ver otros productos disponibles."
        )

    tallas = ", ".join(item["tallas"])
    PEDIDOS.append({
        "cliente": numero_cliente,
        "producto": item["nombre"],
        "precio": item["precio"],
        "estado": "pendiente confirmación"
    })

    return (
        f"¡Perfecto! Anotamos tu pedido 🎉\n\n"
        f"📦 *{item['nombre']}*\n"
        f"💰 S/ {item['precio']}\n"
        f"📏 Tallas disponibles: {tallas}\n\n"
        "Un asesor te contactará en breve para confirmar talla y coordinar el pago.\n\n"
        "¿Algo más? Escribe *menu* para volver al inicio."
    )

def ver_pedidos(numero_cliente):
    pedidos_cliente = [p for p in PEDIDOS if p["cliente"] == numero_cliente]
    if not pedidos_cliente:
        return "No tienes pedidos registrados aún. Escribe *3* para hacer tu primer pedido. 🛍️"
    texto = "📋 *Tus pedidos:*\n\n"
    for i, p in enumerate(pedidos_cliente, 1):
        texto += f"{i}. {p['producto']} — S/ {p['precio']} ({p['estado']})\n"
    return texto

def procesar_mensaje(mensaje, numero_cliente):
    msg = mensaje.strip().lower()

    if any(saludo in msg for saludo in ["hola", "buenas", "buenos", "hi", "hello", "inicio", "menu", "menú", "start"]):
        return obtener_menu()

    if msg == "1" or "catalogo" in msg or "catálogo" in msg or "productos" in msg:
        return obtener_catalogo()

    if msg == "2" or "precio" in msg or "cuanto" in msg or "cuánto" in msg or "cuesta" in msg:
        if msg == "2":
            return "¿De qué producto quieres saber el precio? Escribe el nombre. 👇\n\nEjemplo: *precio polo* o *cuánto cuesta el jean*"
        return consultar_precio(msg)

    if msg == "3" or "pedir" in msg or "quiero" in msg or "comprar" in msg or "pedido" in msg:
        return iniciar_pedido(msg, numero_cliente)

    if msg == "4" or "mis pedidos" in msg or "ver pedidos" in msg:
        return ver_pedidos(numero_cliente)

    for clave in CATALOGO.keys():
        if clave in msg:
            return consultar_precio(msg)

    return (
        "No entendí bien tu mensaje 😅\n\n"
        "Escribe *menu* para ver las opciones disponibles."
    )

def lambda_handler(event, context):
    try:
        body = event.get("body", "")
        if event.get("isBase64Encoded", False):
            import base64
            body = base64.b64decode(body).decode("utf-8")

        params = urllib.parse.parse_qs(body)
        mensaje_entrante = params.get("Body", [""])[0]
        numero_cliente = params.get("From", ["desconocido"])[0]

        respuesta_texto = procesar_mensaje(mensaje_entrante, numero_cliente)

        resp = MessagingResponse()
        resp.message(respuesta_texto)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/xml"},
            "body": str(resp)
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        resp = MessagingResponse()
        resp.message("Ocurrió un error. Por favor intenta nuevamente.")
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/xml"},
            "body": str(resp)
        }
