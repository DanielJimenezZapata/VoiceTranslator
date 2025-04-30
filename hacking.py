import os
import socket
import hashlib
from datetime import datetime
#10.33.17.132
def analizar_puertos(host, puertos):
    print(f"\n[+] Escaneando puertos en {host}...")
    for puerto in puertos:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        resultado = sock.connect_ex((host, puerto))
        if resultado == 0:
            print(f"  [+] Puerto {puerto} está ABIERTO")
        else:
            print(f"  [-] Puerto {puerto} está CERRADO")
        sock.close()

def calcular_hash(archivo):
    if os.path.exists(archivo):
        with open(archivo, "rb") as f:
            bytes = f.read()
            md5 = hashlib.md5(bytes).hexdigest()
            sha256 = hashlib.sha256(bytes).hexdigest()
            print(f"\n[+] Hash MD5:    {md5}")
            print(f"[+] Hash SHA256: {sha256}")
    else:
        print("[!] Archivo no encontrado.")

def guardar_log(mensaje):
    with open("seguridad.log", "a") as log:
        log.write(f"{datetime.now()} - {mensaje}\n")

if __name__ == "__main__":
    print("🔍 Analizador de Seguridad Básico 🔍")
    print("1. Escanear puertos")
    print("2. Calcular hash de un archivo")
    print("3. Salir")

    opcion = input("Selecciona una opción: ")

    if opcion == "1":
        host = input("Ingresa la dirección IP o dominio: ")
        puertos = [21, 22, 80, 443, 3306, 8080]  # Puertos comunes
        analizar_puertos(host, puertos)
        guardar_log(f"Escaneo de puertos en {host}")
    elif opcion == "2":
        archivo = input("Ingresa la ruta del archivo: ")
        calcular_hash(archivo)
        guardar_log(f"Hash calculado para {archivo}")
    elif opcion == "3":
        print("Saliendo...")
    else:
        print("Opción no válida.")