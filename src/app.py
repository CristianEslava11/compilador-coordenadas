import socket
import threading
import time

import uvicorn
import webview

# servidor.py expone la API y además sirve la interfaz en /ui/,
# así la ventana siempre habla con el backend de esta misma instancia.
from servidor import app as fastapi_app

HOST = "127.0.0.1"


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
