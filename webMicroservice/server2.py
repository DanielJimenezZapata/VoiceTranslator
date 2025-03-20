from flask import Flask, render_template, jsonify, request, session
import speech_recognition as sr
from deep_translator import GoogleTranslator
import threading
import uuid
import pyttsx3  # Para síntesis de voz

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Clave para sesiones

# Diccionario para almacenar datos por usuario
usuarios = {}

# Función para obtener un ID único por usuario
def obtener_usuario():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())  # Genera un ID único
    return session["user_id"]

# Función para traducir texto
def traducir_texto(texto):
    return GoogleTranslator(source="es", target="zh-CN").translate(texto)

# Configura el motor de síntesis de voz
def configurar_motor():
    motor = pyttsx3.init()
    motor.setProperty("rate", 150)  # Configura la velocidad de habla
    motor.setProperty("volume", 1)  # Configura el volumen
    return motor

# Función para reconocer audio y traducirlo
def reconocer_audio(user_id):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while usuarios[user_id]["escuchando"]:
            try:
                print(f"🎙 Escuchando para {user_id}...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                if not usuarios[user_id]["escuchando"]:
                    break
                texto = recognizer.recognize_google(audio, language="es-ES")
                if texto:
                    print(f"🗣 Texto reconocido ({user_id}): {texto}")
                    usuarios[user_id]["texto_espanol"] += " " + texto
                    traduccion = traducir_texto(texto)
                    usuarios[user_id]["texto_chino"] += " " + traduccion
                    print(f"🇨🇳 Traducción ({user_id}): {traduccion}")
            except sr.UnknownValueError:
                print("🔇 No se entendió el audio...")
            except sr.WaitTimeoutError:
                print("⏳ Tiempo agotado, volviendo a escuchar...")
            except sr.RequestError:
                print("⚠️ Error con el servicio de reconocimiento de voz.")
        print(f"⛔ Escucha detenida para {user_id}.")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/estado")
def obtener_estado():
    user_id = obtener_usuario()
    if user_id not in usuarios:
        usuarios[user_id] = {"texto_espanol": "", "texto_chino": "", "escuchando": False}
    return jsonify(usuarios[user_id])

@app.route("/iniciar", methods=["POST"])
def iniciar_escucha():
    user_id = obtener_usuario()
    if user_id not in usuarios:
        usuarios[user_id] = {"texto_espanol": "", "texto_chino": "", "escuchando": False}
    if not usuarios[user_id]["escuchando"]:
        usuarios[user_id]["escuchando"] = True
        hilo_escucha = threading.Thread(target=reconocer_audio, args=(user_id,), daemon=True)
        hilo_escucha.start()
    return jsonify({"mensaje": "Escucha iniciada", "escuchando": True}), 200

@app.route("/detener", methods=["POST"])
def detener_escucha():
    user_id = obtener_usuario()
    if user_id in usuarios:
        usuarios[user_id]["escuchando"] = False
    return jsonify({"mensaje": "Escucha detenida", "escuchando": False}), 200

@app.route("/hablar", methods=["POST"])
def hablar_texto():
    user_id = obtener_usuario()
    if user_id not in usuarios or not usuarios[user_id]["texto_chino"]:
        return jsonify({"error": "No hay texto para reproducir"}), 400
    return jsonify({"texto_chino": usuarios[user_id]["texto_chino"]}), 200

@app.route("/limpiar", methods=["POST"])
def limpiar_texto():
    user_id = obtener_usuario()
    if user_id in usuarios:
        usuarios[user_id]["texto_espanol"] = ""
        usuarios[user_id]["texto_chino"] = ""
    return jsonify({"mensaje": "Textos limpiados"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8501)