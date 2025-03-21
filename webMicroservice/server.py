from flask import Flask, render_template, jsonify, request, session
import speech_recognition as sr
from deep_translator import GoogleTranslator
import threading
import uuid
import pyttsx3 

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Clave para sesiones

# Diccionario para almacenar datos por usuario
usuarios = {}

# Función para obtener un ID único por usuario
def obtener_usuario():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())  # Genera un ID único
    return session["user_id"]

def traducir_texto(texto, idioma_origen, idioma_destino):
    return GoogleTranslator(source=idioma_origen, target=idioma_destino).translate(texto)

# Configura el motor de síntesis de voz
def configurar_motor():
    motor = pyttsx3.init()
    motor.setProperty("rate", 150)  # Configura la velocidad de habla
    motor.setProperty("volume", 1)  # Configura el volumen
    return motor

# Función para reconocer audio y traducirlo
def reconocer_audio(user_id, idioma_origen, idioma_destino):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while usuarios[user_id]["escuchando"]:
            try:
                print(f"🎙 Escuchando para {user_id}...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                if not usuarios[user_id]["escuchando"]:
                    break
                texto = recognizer.recognize_google(audio, language=idioma_origen)
                if texto:
                    print(f"🗣 Texto reconocido ({user_id}): {texto}")
                    # Acumulamos el texto en el idioma de origen
                    usuarios[user_id]["texto_origen"] += " " + texto
                    traduccion = traducir_texto(texto, idioma_origen, idioma_destino)
                    # Acumulamos la traducción
                    usuarios[user_id]["texto_traducido"] += " " + traduccion
                    print(f"🌍 Traducción ({user_id}): {traduccion}")
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
        usuarios[user_id] = {"texto_origen": "", "texto_traducido": "", "escuchando": False}
    return jsonify(usuarios[user_id])

@app.route("/iniciar", methods=["POST"])
def iniciar_escucha():
    try:
        user_id = obtener_usuario()
        if user_id not in usuarios:
            usuarios[user_id] = {"texto_origen": "", "texto_traducido": "", "escuchando": False}
        
        if not usuarios[user_id]["escuchando"]:
            data = request.get_json()
            idioma_origen = data.get("idioma_origen", "es")  # Por defecto español
            idioma_destino = data.get("idioma_destino", "zh-CN")  # Por defecto chino
            usuarios[user_id]["escuchando"] = True
            hilo_escucha = threading.Thread(target=reconocer_audio, args=(user_id, idioma_origen, idioma_destino), daemon=True)
            hilo_escucha.start()
        return jsonify({"mensaje": "Escucha iniciada", "escuchando": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/detener", methods=["POST"])
def detener_escucha():
    user_id = obtener_usuario()
    if user_id in usuarios:
        usuarios[user_id]["escuchando"] = False
    return jsonify({"mensaje": "Escucha detenida", "escuchando": False}), 200

@app.route("/hablar", methods=["POST"])
def hablar_texto():
    user_id = obtener_usuario()
    if user_id not in usuarios or not usuarios[user_id]["texto_traducido"]:
        return jsonify({"error": "No hay texto para reproducir"}), 400
    return jsonify({"texto_traducido": usuarios[user_id]["texto_traducido"]}), 200

@app.route("/limpiar", methods=["POST"])
def limpiar_texto():
    user_id = obtener_usuario()
    if user_id in usuarios:
        usuarios[user_id]["texto_origen"] = ""
        usuarios[user_id]["texto_traducido"] = ""
    return jsonify({"mensaje": "Textos limpiados"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8501)