from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index2.html')

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.get_json()
    text = data.get('text', '')
    source_lang = data.get('source_lang', 'es')
    target_lang = data.get('target_lang', 'zh-CN')
    
    try:
        translated_text = GoogleTranslator(
            source=source_lang, 
            target=target_lang
        ).translate(text)
        return jsonify({'translated_text': translated_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8501)