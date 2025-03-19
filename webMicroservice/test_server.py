import unittest
import json
import server  # Importamos todo el módulo para modificar las variables globales

class TestFlaskApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ Configuración inicial antes de ejecutar las pruebas """
        cls.client = server.app.test_client()

    def setUp(self):
        """ Se ejecuta antes de cada test para restablecer el estado """
        setattr(server, "texto_espanol", "Hola, esto es una prueba.")
        setattr(server, "texto_chino", "你好，这是一个测试。")
        setattr(server, "escuchando", False)  # Asegurar que siempre inicie apagado

    def test_homepage(self):
        """ Prueba si la página principal carga correctamente """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Traductor de Voz', response.data)

    def test_estado(self):
        """ Prueba si el estado de la aplicación se obtiene correctamente """
        response = self.client.get('/estado')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["texto_espanol"], "Hola, esto es una prueba.")
        self.assertEqual(data["texto_chino"], "你好，这是一个测试。")
        self.assertFalse(data["escuchando"])

    def test_iniciar_escucha(self):
        """ Prueba el endpoint de iniciar escucha """
        response = self.client.post('/iniciar')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['escuchando'])

    def test_detener_escucha(self):
        """ Prueba el endpoint de detener escucha """
        response = self.client.post('/detener')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data['escuchando'])

    def test_hablar(self):
        """ Prueba el endpoint de síntesis de voz con texto simulado """
        response = self.client.post('/hablar')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["mensaje"], "Reproduciendo voz")

if __name__ == '__main__':
    unittest.main()
