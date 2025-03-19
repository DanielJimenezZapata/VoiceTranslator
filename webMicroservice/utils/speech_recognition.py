import threading
import speech_recognition as sr
from utils.translator import traducir_texto

recognizer = sr.Recognizer()
texto_espanol = ""
texto_chino = ""
escuchando = False

def reconocer_audio():
    """Captura el audio y lo traduce al chino."""
    global texto_espanol, texto_chino, escuchando
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while escuchando:
            try:
                print("🎙 Escuchando...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                if not escuchando:
                    break
                texto = recognizer.recognize_google(audio, language="es-ES")
                if texto:
                    print(f"🗣 Texto reconocido: {texto}")
                    texto_espanol += " " + texto
                    traduccion = traducir_texto(texto)
                    texto_chino += " " + traduccion
                    print(f"🇨🇳 Traducción: {traduccion}")
            except sr.UnknownValueError:
                print("🔇 No se entendió el audio...")
            except sr.WaitTimeoutError:
                print("⏳ Tiempo agotado, volviendo a escuchar...")
            except sr.RequestError:
                print("⚠️ Error con el servicio de reconocimiento de voz.")
        print("⛔ Escucha detenida.")

def iniciar_reconocimiento():
    """Inicia el reconocimiento en un hilo."""
    global escuchando
    if not escuchando:
        escuchando = True
        threading.Thread(target=reconocer_audio, daemon=True).start()

def detener_reconocimiento():
    """Detiene el reconocimiento."""
    global escuchando
    escuchando = False

def limpiar_texto():
    """Limpia los textos en español y chino."""
    global texto_espanol, texto_chino
    texto_espanol = ""
    texto_chino = ""
