from flask import Flask, render_template, jsonify
import speech_recognition as sr
from deep_translator import GoogleTranslator
import threading

app = Flask(__name__)

recognizer = sr.Recognizer()
texto_espanol = ""
texto_chino = ""
escuchando = False

def traducir_texto(texto):
    """Traduce el texto de español a chino."""
    return GoogleTranslator(source="es", target="en").translate(texto)

def reconocer_audio():
    """Captura audio continuamente mientras `escuchando` sea True."""
    global texto_espanol, texto_chino, escuchando
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            if not escuchando:
                continue
            try:
                print("🎙 Escuchando...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
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

# Iniciar el hilo de escucha en segundo plano
thread = threading.Thread(target=reconocer_audio, daemon=True)
thread.start()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/estado")
def obtener_estado():
    """Devuelve el estado actual de la transcripción y si la escucha está activa."""
    return jsonify({
        "texto_espanol": texto_espanol.strip(),
        "texto_chino": texto_chino.strip(),
        "escuchando": escuchando
    })

@app.route("/iniciar", methods=["POST"])
def iniciar_escucha():
    """Inicia la escucha de voz."""
    global escuchando
    escuchando = True
    return jsonify({"mensaje": "Escucha iniciada", "escuchando": True}), 200

@app.route("/detener", methods=["POST"])
def detener_escucha():
    """Detiene la escucha de voz."""
    global escuchando
    escuchando = False
    return jsonify({"mensaje": "Escucha detenida", "escuchando": False}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8501)
