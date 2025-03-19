from flask import Blueprint, render_template, jsonify

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    """Carga la página principal."""
    return render_template("index.html")

@main_bp.route("/estado")
def obtener_estado():
    """Devuelve el estado actual de la transcripción."""
    from utils.speech_recognition import texto_espanol, texto_chino, escuchando
    return jsonify({
        "texto_espanol": texto_espanol.strip(),
        "texto_chino": texto_chino.strip(),
        "escuchando": escuchando
    })
