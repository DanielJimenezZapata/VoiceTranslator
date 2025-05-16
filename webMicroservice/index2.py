from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator
import logging

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    logger.info("Serving home page")
    return render_template('index2.html')

@app.route('/translate', methods=['POST'])
def translate_text():
    logger.info("--- Nuevo bloque de traducción recibido ---")
    
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        logger.info(f"Texto recibido ({len(text.split())} palabras): {text[:100]}{'...' if len(text) > 100 else ''}")
        
        if not text:
            logger.warning("Texto vacío recibido")
            return jsonify({'error': 'No text provided'}), 400
            
        try:
            translated_text = GoogleTranslator(
                source=data.get('source_lang', 'es'), 
                target=data.get('target_lang', 'en')
            ).translate(text)
            
            logger.info(f"Traducción exitosa ({len(translated_text.split())} palabras)")
            return jsonify({
                'translated_text': translated_text,
                'status': 'success'
            })
            
        except Exception as translate_error:
            logger.error(f"Error en traducción: {str(translate_error)}")
            return jsonify({'error': str(translate_error)}), 400
            
    except Exception as request_error:
        logger.error(f"Error procesando solicitud: {str(request_error)}")
        return jsonify({'error': 'Invalid request data'}), 400

if __name__ == '__main__':
    logger.info("Iniciando servidor Flask...")
    app.run(debug=True, host='0.0.0.0', port=8501, ssl_context='adhoc')