import os
from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator
import logging
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Configuración del servidor de archivos CON RESTRICCIONES
class RestrictedHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Lista de directorios prohibidos
        blocked_paths = [
            "Windows", "Program Files", "Program Files (x86)",
            "Users", "ProgramData", "System Volume Information",
            "Config.Msi", "Recovery", "$Recycle.Bin"
        ]
        
        # Verificar si el path solicitado contiene directorios prohibidos
        if any(blocked.lower() in self.path.lower() for blocked in blocked_paths):
            self.send_error(403, "Forbidden: Access to system directories is restricted")
            logger.warning(f"Intento de acceso bloqueado a: {self.path}")
            return
        
        # Registrar accesos (para auditoría de seguridad)
        logger.info(f"Acceso permitido a: {self.path}")
        super().do_GET()

def run_file_server():
    base_path = "C:\\"
    
    if not os.path.exists(base_path):
        logger.error("No se encontró la unidad C:\\")
        return
    
    os.chdir(base_path)
    server_address = ('localhost', 8000)  # ¡MANTENER solo en localhost!
    httpd = HTTPServer(server_address, RestrictedHandler)
    logger.critical("¡ADVERTENCIA DE SEGURIDAD! Servidor de archivos iniciado en C:\\")
    logger.critical("ESTÁS EXPONIENDO INFORMACIÓN SENSIBLE DEL SISTEMA")
    httpd.serve_forever()

# Configuración de Flask
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
                        
                        translated_parts.append(translated)
                    except Exception as part_error:
                        logger.error(f"Error traduciendo parte {i}: {str(part_error)}")
                        raise part_error
                
                translated_text = ' '.join(translated_parts)
                logger.info(f"Texto largo traducido exitosamente (partes: {len(parts)})")
            else:
                translated_text = GoogleTranslator(
                    source=source_lang, 
                    target=target_lang
                ).translate(text)
                logger.info("Texto traducido exitosamente")
            
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

if __name__ == '__main__':
    # Iniciar el servidor de archivos en un hilo separado
    file_server_thread = threading.Thread(target=run_file_server, daemon=True)
    file_server_thread.start()
    
    # Iniciar el servidor Flask
    logger.info("Iniciando servidor Flask...")
    app.run(debug=True, host='0.0.0.0', port=8501)