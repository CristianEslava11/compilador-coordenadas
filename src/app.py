import os
import socket
import sys
import threading
import time

import uvicorn
import webview
from fastapi.staticfiles import StaticFiles

from servidor import app as fastapi_app

HOST = "127.0.0.1"

# Carpeta base: dentro del .exe de PyInstaller los archivos se extraen en sys._MEIPASS
BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

# La UI se sirve desde el mismo servidor que la API (http://HOST:PUERTO/ui/),
# así la interfaz siempre habla con el backend de esta misma instancia.
fastapi_app.mount("/ui", StaticFiles(directory=os.path.join(BASE, "ui"), html=True), name="ui")


def puerto_libre():
    """Pide al sistema operativo un puerto libre, para que varias instancias
    de la app (o un servidor viejo abierto) no choquen en el mismo puerto."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, 0))
        return s.getsockname()[1]


def esperar_servidor(puerto, timeout=10):
    """Espera hasta que el servidor acepte conexiones."""
    limite = time.time() + timeout
    while time.time() < limite:
        try:
            with socket.create_connection((HOST, puerto), timeout=0.2):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def main():
    puerto = puerto_libre()

    # 1. Arrancar FastAPI en hilo daemon (muere cuando cierra la app)
    hilo_servidor = threading.Thread(
        target=uvicorn.run,
        kwargs={"app": fastapi_app, "host": HOST, "port": puerto, "log_level": "warning"},
        daemon=True,
    )
    hilo_servidor.start()

    # 2. Esperar a que el servidor esté listo
    esperar_servidor(puerto)

    # 3. Abrir la ventana nativa con la UI
    webview.create_window(
        title="GeoQuery — Compilador de Coordenadas",
        url=f"http://{HOST}:{puerto}/ui/index.html",
        width=1000,
        height=700,
        resizable=True,
        min_size=(800, 550)
    )
    webview.start(debug=False)      # debug=True para inspeccionar en desarrollo


if __name__ == "__main__":
    main()
