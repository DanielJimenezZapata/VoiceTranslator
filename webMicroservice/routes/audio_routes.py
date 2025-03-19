from flask import Blueprint, jsonify, request
import threading
from utils.speech_recognition import iniciar_reconocimiento, detener_reconocimiento
from utils.text_to_speech import reproducir_voz
from utils.speech_recognition import limpiar_texto

audio_bp = Blueprint("audio", __name__)

@audio_bp.route("/iniciar", methods=["POST"])
def iniciar_escucha():
    """Inicia la grabación de audio en un hilo separado."""
    iniciar_reconocimiento()
    return jsonify({"mensaje": "Escucha iniciada", "escuchando": True}), 200

@audio_bp.route("/detener", methods=["POST"])
def detener_escucha():
    """Detiene la grabación de audio."""
    detener_reconocimiento()
    return jsonify({"mensaje": "Escucha detenida", "escuchando": False}), 200

@audio_bp.route("/hablar", methods=["POST"])
def hablar_texto():
    """Convierte el texto traducido en voz."""
    hilo_voz = threading.Thread(target=reproducir_voz, daemon=True)
    hilo_voz.start()
    return jsonify({"mensaje": "Reproduciendo voz"}), 200

@audio_bp.route("/limpiar", methods=["POST"])
def limpiar():
    """Limpia los textos en español y chino."""
    limpiar_texto()
    return jsonify({"mensaje": "Textos limpiados"}), 200
