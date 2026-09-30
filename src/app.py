import threading
import time
import webview
import uvicorn
from servidor import app as fastapi_app

PUERTO = 8000

def iniciar_servidor():
    """Lanza el servidor FastAPI en un hilo de fondo."""
    uvicorn.run(fastapi_app, host="127.0.0.1", port=PUERTO, log_level="warning")

def main():
    # 1. Arrancar FastAPI en hilo daemon (muere cuando cierra la app)
    hilo_servidor = threading.Thread(target=iniciar_servidor, daemon=True)
    hilo_servidor.start()

    # 2. Esperar brevemente a que el servidor esté listo
    time.sleep(1.5)

    # 3. Abrir la ventana nativa con la UI
    ventana = webview.create_window(
        title="GeoQuery — Compilador de Coordenadas",
        url="ui/index.html",        # ruta relativa a src/
        width=1000,
        height=700,
        resizable=True,
        min_size=(800, 550)
    )
    webview.start(debug=False)      # debug=True para inspeccionar en desarrollo

if __name__ == "__main__":
    main()
