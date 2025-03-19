from flask import Flask
from routes.main_routes import main_bp
from routes.audio_routes import audio_bp

app = Flask(__name__)

# Registrar los Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(audio_bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8501)
