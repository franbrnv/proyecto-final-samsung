import telebot
from transformers import pipeline
import random


TOKEN = "TU_TOKEN_AQUI"  # token de @BotFather
bot = telebot.TeleBot(TOKEN)

# Modelo de análisis de sentimiento en español ya entrenado
analizador = pipeline(
    "sentiment-analysis",
    model="pysentimiento/robertuito-sentiment-analysis"
)

# Funciones 
def generar_respuesta(sentimiento, texto_usuario):
    """Genera respuesta empática según sentimiento y palabras clave"""
    # Frases positivas
    positivas = [
        "¡Que lindo leer eso! Segui así",
        "Me alegra mucho que te sientas así",
        "Que bueno que estes disfrutando"
    ]
    
    # Frases negativas
    negativas = [
        "Uh, que bajon. Contame si queres, te escucho",
        "Uy, suena a que hoy no fue fácil",
        "A veces estos días son duros… estoy acá para escucharte"
    ]
    
    # Frases neutras
    neutras = [
        "Mmm, entiendo… contame un poco mas",
        "Parece un día tranquilo",
        "Ah, interesante… si queres contame mas"
    ]

    texto_lower = texto_usuario.lower()

    # Chequeo de palabras clave antes de usar el sentimiento
    if "triste" in texto_lower or "mal" in texto_lower or "deprimido" in texto_lower:
        return random.choice(negativas)
    elif "feliz" in texto_lower or "contento" in texto_lower or "alegre" in texto_lower:
        return random.choice(positivas)
    elif "normal" in texto_lower or "ok" in texto_lower:
        return random.choice(neutras)

    # Si no hay palabras clave, usar el sentimiento del modelo
    if sentimiento == "POS":
        return random.choice(positivas)
    elif sentimiento == "NEG":
        return random.choice(negativas)
    else:  # NEU
        return random.choice(neutras)


#Respuestas del bot
@bot.message_handler(commands=['start', 'help'])
def bienvenida(message):
    bot.send_message(
        message.chat.id,
        "¡Hola! Soy tu bot que te acompaña emocionalmente\n"
        "Escribi como te sentis y te voy a responder con un mensje amigable.\n\n"
        "Ejemplos:\n"
        "- 'Estoy re feliz hoy'\n"
        "- 'No tengo ganas de nada'\n"
        "- 'Hoy fue un día normal'"
    )

@bot.message_handler(func=lambda message: True)
def analizar_mensaje(message):
    texto = message.text
    bot.send_chat_action(message.chat.id, "typing")

    try:
        resultado = analizador(texto)[0]
        sentimiento = resultado["label"]
        respuesta = generar_respuesta(sentimiento, texto)
    except Exception as e:
        respuesta = f"Hubo un error al analizar tu mensaje: {e}"

    bot.reply_to(message, respuesta)


# Inicio del bot

if __name__ == "__main__":
    print("Bot empático de sentimientos iniciado. Esperando mensajes...")
    bot.infinity_polling()
