import pyttsx3
from utils.speech_recognition import texto_chino

def reproducir_voz():
    """Convierte el texto en chino a voz."""
    if not texto_chino:
        print("⚠️ No hay texto en chino para reproducir.")
        return

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    for voice in voices:
        if "zh" in voice.languages or "chinese" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    engine.setProperty('rate', 150)
    engine.say(texto_chino)
    engine.runAndWait()
