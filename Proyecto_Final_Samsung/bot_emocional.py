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
    texto_lower = texto_usuario.lower()

    # Chequeo de palabras clave antes de usar el sentimiento
    if "estresado" in texto_lower or "frustrado" in texto_lower or "mal" in texto_lower:
        return "Tranquilo, todos empezamos asi. Proba hacer una pausa y volver con otra mirada. Si queres, puedo explicarte paso a paso como seguir."
    elif "enojado" in texto_lower or "molesto" in texto_lower or "fastidioso" in texto_lower:
        return "Uf, entiendo que da bronca. Respira un segundo y contame que parte te esta complicando, seguro lo resolvemos juntos."
    elif "feliz" in texto_lower or "contento" in texto_lower or "alegre" in texto_lower:
        return "¡Genial! Me alegra que te haya salido. Segui asi, vas a aprender un monton."
    elif "no sé" in texto_lower or "confundido" in texto_lower or "nada" in texto_lower:
        return "Esta bien no saberlo todavia. Podemos repasarlo paso a paso si queres, y lo vas a entender mejor."

    # Si no hay palabras clave, usar el sentimiento del modelo
    if sentimiento == "POS":
        return "¡Genial! Me alegra que te haya salido. Segui asi, vas a aprender un monton."
    elif sentimiento == "NEG":
        return "Tranquilo, todos empezamos asi. Proba hacer una pausa y volver con otra mirada. Si queres, puedo explicarte paso a paso como seguir."
    else:  # NEU
        return "Esta bien no saberlo todavia. Podemos repasarlo paso a paso si queres, y lo vas a entender mejor"


#Respuestas del bot
@bot.message_handler(commands=['start', 'help'])
def bienvenida(message):
    bot.send_message(
        message.chat.id,
        "¡Hola! Soy tu bot que te acompaña mientras trabajás con tu computadora 💻\n"
        "Escribí cómo te sentís y te voy a responder con apoyo y consejos.\n\n"
        "Ejemplos:\n"
        "- 'Estoy re feliz porque me salió'\n"
        "- 'No tengo ganas de nada, me frustro'\n"
        "- 'No sé ni por dónde empezar'"
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
    print("Bot emocional de soporte iniciado. Esperando mensajes...")
    bot.infinity_polling()
