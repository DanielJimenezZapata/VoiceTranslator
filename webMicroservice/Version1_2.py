from flask import Flask, render_template, jsonify, request, session
from deep_translator import GoogleTranslator
import uuid
import pyttsx3
from flask_cors import CORS
from datetime import datetime
import threading

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['SESSION_PERMANENT'] = True
CORS(app)

# Configuración de voz
engine = pyttsx3.init()
engine.setProperty('rate', 150)

users = {}

def get_user():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
    
    if session["user_id"] not in users:
        users[session["user_id"]] = {
            "source_text": "",
            "translated_text": "",
            "is_listening": False,
            "last_spoken": ""
        }
    
    return session["user_id"]

def translate_text(text, source_lang, target_lang):
    try:
        return GoogleTranslator(source=source_lang, target=target_lang).translate(text[:5000])
    except Exception as e:
        print(f"Error de traducción: {e}")
        return text

def speak(text, lang):
    try:
        voices = engine.getProperty('voices')
        for voice in voices:
            if lang in voice.id:
                engine.setProperty('voice', voice.id)
                break
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error de voz: {e}")

@app.route("/")
def home():
    return render_template("index1_2.html")

@app.route("/status")
def status():
    user_id = get_user()
    return jsonify(users[user_id])

@app.route("/start", methods=["POST"])
def start():
    user_id = get_user()
    data = request.get_json()
    users[user_id].update({
        "is_listening": True,
        "source_lang": data.get("source_lang", "es"),
        "target_lang": data.get("target_lang", "en")
    })
    return jsonify({"status": "success"})

@app.route("/translate", methods=["POST"])
def translate():
    user_id = get_user()
    data = request.get_json()
    
    text = data.get("text", "")
    is_final = data.get("is_final", False)
    source_lang = data.get("source_lang", "es")
    target_lang = data.get("target_lang", "en")
    
    translated = translate_text(text, source_lang, target_lang)
    
    if is_final:
        users[user_id]["source_text"] += "\n" + text if users[user_id]["source_text"] else text
        users[user_id]["translated_text"] += "\n" + translated if users[user_id]["translated_text"] else translated
        
        # Reproducir automáticamente si es texto nuevo
        if translated != users[user_id]["last_spoken"]:
            threading.Thread(target=speak, args=(translated, target_lang)).start()
            users[user_id]["last_spoken"] = translated
    
    return jsonify({
        "translated_text": translated,
        "is_final": is_final
    })

@app.route("/stop", methods=["POST"])
def stop():
    user_id = get_user()
    users[user_id]["is_listening"] = False
    return jsonify({"status": "success"})

@app.route("/clear", methods=["POST"])
def clear():
    user_id = get_user()
    users[user_id].update({
        "source_text": "",
        "translated_text": "",
        "last_spoken": ""
    })
    return jsonify({"status": "success"})

@app.route("/speak", methods=["POST"])
def speak_endpoint():
    user_id = get_user()
    text = users[user_id].get("translated_text", "")
    lang = users[user_id].get("target_lang", "en")
    
    if text:
        threading.Thread(target=speak, args=(text, lang)).start()
    
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8501)