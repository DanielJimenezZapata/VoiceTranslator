from flask import Flask, render_template, jsonify, request
import speech_recognition as sr
from deep_translator import GoogleTranslator
import threading
import pyttsx3

app = Flask(__name__)

# Inicialización de variables globales
recognizer = sr.Recognizer()
texto_espanol = ""
texto_chino = ""
escuchando = False
hilo_escucha = None

def traducir_texto(texto):
    """Recibe un texto en español y lo traduce al chino usando GoogleTranslator."""
    return GoogleTranslator(source="es", target="zh-CN").translate(texto)

def reconocer_audio():
    """Captura el audio del micrófono y lo convierte en texto.
    Mientras la variable `escuchando` sea True, sigue grabando y procesando audio.
    Luego, traduce el texto reconocido al chino y lo almacena.
    """
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

@app.route("/")
def home():
    """Carga la página principal de la aplicación Flask y renderiza la plantilla HTML."""
    return render_template("index.html")

@app.route("/estado")
def obtener_estado():
    """Devuelve el estado actual de la transcripción."""
    return jsonify({
        "texto_espanol": texto_espanol.strip(),
        "texto_chino": texto_chino.strip(),
        "escuchando": escuchando
    })

@app.route("/iniciar", methods=["POST"])
def iniciar_escucha():
    """Inicia la grabación de audio en un hilo separado."""
    global escuchando, hilo_escucha
    if not escuchando:
        escuchando = True
        hilo_escucha = threading.Thread(target=reconocer_audio, daemon=True)
        hilo_escucha.start()
    return jsonify({"mensaje": "Escucha iniciada", "escuchando": True}), 200

@app.route("/detener", methods=["POST"])
def detener_escucha():
    """Detiene la grabación de audio."""
    global escuchando
    escuchando = False
    return jsonify({"mensaje": "Escucha detenida", "escuchando": False}), 200

@app.route("/hablar", methods=["POST"])
def hablar_texto():
    """Convierte en voz el texto traducido al chino y lo reproduce en un hilo separado."""
    global texto_chino

    def reproducir_voz():
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
    
    hilo_voz = threading.Thread(target=reproducir_voz, daemon=True)
    hilo_voz.start()

    return jsonify({"mensaje": "Reproduciendo voz"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8501)
