from flask import Flask, render_template, jsonify, request, session
import speech_recognition as sr
from deep_translator import GoogleTranslator
import threading
import pyttsx3
import uuid

app = Flask(__name__)
app.secret_key = "supersecreto"  # Necesario para manejar sesiones

# Diccionario para almacenar datos de cada usuario
usuarios = {}

def generar_id_usuario():
    """Genera un ID único para cada usuario"""
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())  # Generar un UUID único
    return session["user_id"]

def traducir_texto(texto):
    """Recibe un texto en español y lo traduce al chino usando GoogleTranslator."""
    return GoogleTranslator(source="es", target="zh-CN").translate(texto)

def reconocer_audio(user_id):
    """Captura el audio del micrófono y lo convierte en texto solo para el usuario específico."""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        
        while usuarios[user_id]["escuchando"]:
            try:
                print(f"🎙 Escuchando para usuario {user_id}...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                if not usuarios[user_id]["escuchando"]:
                    break

                texto = recognizer.recognize_google(audio, language="es-ES")
                if texto:
                    print(f"🗣 Texto reconocido: {texto}")
                    usuarios[user_id]["texto_espanol"] += " " + texto
                    traduccion = traducir_texto(texto)
                    usuarios[user_id]["texto_chino"] += " " + traduccion
                    print(f"🇨🇳 Traducción: {traduccion}")

            except sr.UnknownValueError:
                print("🔇 No se entendió el audio...")
            except sr.WaitTimeoutError:
                print("⏳ Tiempo agotado, volviendo a escuchar...")
            except sr.RequestError:
                print("⚠️ Error con el servicio de reconocimiento de voz.")

@app.route("/")
def home():
    """Carga la página principal y asigna un ID de usuario único."""
    generar_id_usuario()
    return render_template("index.html")

@app.route("/estado")
def obtener_estado():
    """Devuelve el estado actual de la transcripción del usuario."""
    user_id = generar_id_usuario()
    if user_id not in usuarios:
        return jsonify({"error": "No hay datos para este usuario"}), 400

    return jsonify({
        "texto_espanol": usuarios[user_id]["texto_espanol"].strip(),
        "texto_chino": usuarios[user_id]["texto_chino"].strip(),
        "escuchando": usuarios[user_id]["escuchando"]
    })

@app.route("/iniciar", methods=["POST"])
def iniciar_escucha():
    """Inicia la grabación de audio solo para el usuario actual."""
    user_id = generar_id_usuario()
    if user_id not in usuarios:
        usuarios[user_id] = {"texto_espanol": "", "texto_chino": "", "escuchando": False}

    if not usuarios[user_id]["escuchando"]:
        usuarios[user_id]["escuchando"] = True
        hilo_escucha = threading.Thread(target=reconocer_audio, args=(user_id,), daemon=True)
        hilo_escucha.start()

    return jsonify({"mensaje": "Escucha iniciada", "escuchando": True}), 200

@app.route("/detener", methods=["POST"])
def detener_escucha():
    """Detiene la grabación de audio solo para el usuario actual."""
    user_id = generar_id_usuario()
    if user_id in usuarios:
        usuarios[user_id]["escuchando"] = False

    return jsonify({"mensaje": "Escucha detenida", "escuchando": False}), 200

@app.route("/hablar", methods=["POST"])
def hablar_texto():
    """Convierte en voz el texto traducido del usuario y lo reproduce."""
    user_id = generar_id_usuario()
    if user_id not in usuarios or not usuarios[user_id]["texto_chino"]:
        return jsonify({"error": "No hay texto para reproducir"}), 400

    def reproducir_voz():
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')

        for voice in voices:
            if "zh" in voice.languages or "chinese" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break

        engine.setProperty('rate', 150)
        engine.say(usuarios[user_id]["texto_chino"])
        engine.runAndWait()

    hilo_voz = threading.Thread(target=reproducir_voz, daemon=True)
    hilo_voz.start()

    return jsonify({"mensaje": "Reproduciendo voz"}), 200

@app.route("/limpiar", methods=["POST"])
def limpiar_texto():
    """Limpia los textos solo del usuario actual."""
    user_id = generar_id_usuario()
    if user_id in usuarios:
        usuarios[user_id]["texto_espanol"] = ""
        usuarios[user_id]["texto_chino"] = ""

    return jsonify({"mensaje": "Textos limpiados"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8501)
