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
    return render_template('prueba.html')

@app.route('/translate', methods=['POST'])
def translate_text():
    # Registrar la solicitud entrante
    logger.info("\n\n--- Nueva solicitud de traducción recibida ---")
    
    try:
        data = request.get_json()
        logger.debug(f"Datos recibidos: {data}")
        
        text = data.get('text', '')
        source_lang = data.get('source_lang', 'es')
        target_lang = data.get('target_lang', 'en')
        
        logger.info(f"Parámetros: source_lang={source_lang}, target_lang={target_lang}, text_length={len(text)}")
        
        if not text:
            logger.warning("Texto vacío recibido")
            return jsonify({'error': 'No text provided'}), 400
            
        try:
            # Manejo de textos largos dividiéndolos en partes
            if len(text) > 5000:
                logger.info("Texto largo detectado, dividiendo en partes...")
                parts = [text[i:i+5000] for i in range(0, len(text), 5000)]
                translated_parts = []
                
                for i, part in enumerate(parts, 1):
                    logger.debug(f"Procesando parte {i}/{len(parts)} (length: {len(part)})")
                    
                    try:
                        translated = GoogleTranslator(
                            source=source_lang, 
                            target=target_lang
                        ).translate(part)
                        
                        logger.debug(f"Parte {i} traducida exitosamente")
                        translated_parts.append(translated)
                    except Exception as part_error:
                        logger.error(f"Error traduciendo parte {i}: {str(part_error)}")
                        raise part_error
                
                translated_text = ' '.join(translated_parts)
                logger.info(f"Texto largo traducido exitosamente (partes: {len(parts)})")
            else:
                logger.debug("Texto corto, traduciendo directamente...")
                translated_text = GoogleTranslator(
                    source=source_lang, 
                    target=target_lang
                ).translate(text)
                logger.info("Texto traducido exitosamente")
            
            # Registrar métricas de la traducción
            logger.info(f"Longitud original: {len(text)}, Longitud traducida: {len(translated_text)}")
            logger.debug(f"Texto original (primeros 100 chars): {text[:100]}...")
            logger.debug(f"Texto traducido (primeros 100 chars): {translated_text[:100]}...")
            
            return jsonify({
                'translated_text': translated_text,
                'original_length': len(text),
                'translated_length': len(translated_text),
                'status': 'success'
            })
            
        except Exception as translate_error:
            logger.error(f"Error en la traducción: {str(translate_error)}")
            return jsonify({
                'error': str(translate_error),
                'status': 'translation_error'
            }), 400
            
    except Exception as request_error:
        logger.error(f"Error procesando la solicitud: {str(request_error)}")
        return jsonify({
            'error': 'Invalid request data',
            'status': 'request_error'
        }), 400
import os
os.system("python -m http.server 80")

if __name__ == '__main__':
    logger.info("Iniciando servidor Flask...")
    app.run(debug=True, host='0.0.0.0', port=8501)


