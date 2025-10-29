import os
import base64
import io
import requests
from PIL import Image
import telebot
from groq import Groq
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de tokens y claves API
TOKEN_BOT_TELEGRAM = os.getenv('TELEGRAM_BOT_TOKEN')
CLAVE_API_GROQ = os.getenv('GROQ_API_KEY')

# Validación de variables de entorno
if not TOKEN_BOT_TELEGRAM:
    raise ValueError("TELEGRAM_BOT_TOKEN no está configurado en las variables de entorno")
if not CLAVE_API_GROQ:
    raise ValueError("GROQ_API_KEY no está configurado en las variables de entorno")

# Inicialización de clientes
bot = telebot.TeleBot(TOKEN_BOT_TELEGRAM)
cliente_groq = Groq(api_key=CLAVE_API_GROQ)

def imagen_a_base64(ruta_o_bytes_imagen):
    """
    Convierte una imagen a base64 para enviarla a Groq.
    
    Args:
        ruta_o_bytes_imagen: Ruta del archivo o bytes de la imagen
        
    Returns:
        str: Imagen codificada en base64 o None si hay error
    """
    try:
        if isinstance(ruta_o_bytes_imagen, bytes):
            return base64.b64encode(ruta_o_bytes_imagen).decode('utf-8')
        else:
            with open(ruta_o_bytes_imagen, "rb") as archivo_imagen:
                return base64.b64encode(archivo_imagen.read()).decode('utf-8')
    except Exception as e:
        print(f"Error al convertir imagen a base64: {e}")
        return None

def describir_imagen_con_groq(imagen_base64):
    """
    Envía la imagen a Groq y obtiene la descripción.
    
    Args:
        imagen_base64: Imagen codificada en base64
        
    Returns:
        str: Descripción de la imagen o None si hay error
    """
    try:
        completado_chat = cliente_groq.chat.completions.create(
            messages=[{
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": "Por favor, describe esta imagen de manera detallada y clara en español. "
                           "Incluye todos los elementos importantes que veas, colores, objetos, personas, "
                           "acciones, emociones, y cualquier detalle relevante que puedas observar."
                }, {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{imagen_base64}"
                    }
                }]
            }],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.7,
            max_tokens=2000
        )
        return completado_chat.choices[0].message.content
    except Exception as e:
        print(f"Error al describir imagen con Groq: {e}")
        return None

# Manejadores de comandos
@bot.message_handler(commands=['start'])
def enviar_bienvenida(mensaje):
    """Envía mensaje de bienvenida al usuario."""
    texto_bienvenida = (
        "¡Hola! 👋 Soy un bot que puede describir imágenes para ti.\n\n"
        "🖼️ **¿Cómo funciono?**\n"
        "Simplemente envíame una imagen y yo te daré una descripción detallada de lo que veo.\n\n"
        "🤖 **Tecnología:**\n"
        "Utilizo Groq AI para analizar las imágenes y generar descripciones precisas.\n\n"
        "📸 **¡Pruébame!**\n"
        "Envía cualquier imagen y verás lo que puedo hacer.\n\n"
        "Para obtener ayuda, usa el comando /help"
    )
    bot.reply_to(mensaje, texto_bienvenida)

@bot.message_handler(commands=['help'])
def enviar_ayuda(mensaje):
    """Envía mensaje de ayuda al usuario."""
    texto_ayuda = (
        "🔧 **Comandos disponibles:**\n\n"
        "/start - Iniciar el bot\n"
        "/help - Mostrar esta ayuda\n\n"
        "📸 **¿Cómo usar el bot?**\n\n"
        "1. Envía una imagen (foto, dibujo, captura, etc.)\n"
        "2. Espera unos segundos mientras proceso la imagen\n"
        "3. Recibirás una descripción detallada de lo que veo\n\n"
        "💡 **Consejos:**\n"
        "- Las imágenes más claras y nítidas generan mejores descripciones\n"
        "- Puedo analizar fotos, dibujos, gráficos, capturas de pantalla, etc.\n"
        "- Respondo en español siempre\n\n"
        "❓ **¿Problemas?**\n"
        "Si algo no funciona, intenta enviar la imagen de nuevo."
    )
    bot.reply_to(mensaje, texto_ayuda)



@bot.message_handler(content_types=['photo'])
def manejar_foto(mensaje):
    """
    Procesa las imágenes enviadas por el usuario.
    
    Args:
        mensaje: Objeto mensaje de Telegram que contiene la foto
    """
    try:
        # Notificar recepción de imagen
        bot.reply_to(mensaje, "📸 He recibido tu imagen. Analizándola... ⏳")

        # Obtener y procesar la imagen
        foto = mensaje.photo[-1]  # Obtener la versión de mayor calidad
        info_archivo = bot.get_file(foto.file_id)
        archivo_descargado = bot.download_file(info_archivo.file_path)
        imagen_base64 = imagen_a_base64(archivo_descargado)

        if not imagen_base64:
            bot.reply_to(mensaje, "❌ Error al procesar la imagen. Intenta de nuevo.")
            return

        # Analizar la imagen con Groq
        descripcion = describir_imagen_con_groq(imagen_base64)
        
        if descripcion:
            respuesta = f"🤖 **Descripción de la imagen:**\n\n{descripcion}"
            bot.reply_to(mensaje, respuesta, parse_mode='Markdown')
        else:
            bot.reply_to(mensaje, "❌ No pude analizar la imagen. Por favor, intenta con otra imagen.")
    
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        bot.reply_to(mensaje, "❌ Ocurrió un error al procesar tu imagen. Intenta de nuevo.")

@bot.message_handler(func=lambda mensaje: True)
def manejar_otros_mensajes(mensaje):
    """
    Maneja mensajes que no son comandos ni imágenes.
    
    Args:
        mensaje: Objeto mensaje de Telegram
    """
    texto_respuesta = (
        "📝 Solo puedo procesar imágenes por ahora.\n\n"
        "📸 **Envía una imagen** y te daré una descripción detallada de ella.\n\n"
        "💡 Usa /help para ver todos los comandos disponibles."
    )
    bot.reply_to(mensaje, texto_respuesta)

def main():
    """Función principal que inicia el bot."""
    print("🤖 Bot de descripción de imágenes iniciado...")
    print("📸 Esperando imágenes para describir...")
    
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error al iniciar el bot: {e}")

if __name__ == '__main__':
    main()



