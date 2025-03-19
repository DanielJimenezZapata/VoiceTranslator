from deep_translator import GoogleTranslator

def traducir_texto(texto):
    """Traduce un texto del español al chino."""
    return GoogleTranslator(source="es", target="zh-CN").translate(texto)
