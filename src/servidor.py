import os

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from Compilador import compilar_programa

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="GeoQuery", description="API para ejecutar el programa de lenguaje de coordenadas", version="1.0.0")


@app.middleware("http")
async def revalidar_interfaz(request, call_next):
	# Obliga al navegador a comprobar si los archivos de la interfaz cambiaron (responde 304
	# si no), para que después de una actualización nadie se quede con el CSS/JS viejo
	respuesta = await call_next(request)
	if request.url.path.startswith("/ui"):
		respuesta.headers["Cache-Control"] = "no-cache"
	return respuesta


class CodigoRequest(BaseModel):
	codigo: str



@app.get("/", include_in_schema=False)
def inicio():
	# Al abrir la URL del servicio en el navegador se muestra directamente la interfaz
	return RedirectResponse(url="/ui/")


@app.get("/info")
def info():
	return {"lenguaje":"GEO",
			"version":"1.0.0",
			"estado":"en desarrollo",
			"datos_geograficos":"© OpenStreetMap contributors (Nominatim)"}


@app.post("/iniciar")
def ejecutar_codigo(request: CodigoRequest):
    # Una instrucción por línea; se ignoran las líneas vacías y los comentarios (#).
    # Cada instrucción pasa por las fases léxica, sintáctica, semántica y de ejecución.
    instrucciones = compilar_programa(request.codigo)

    if not instrucciones:
        return {"exito": False, "error": "No se ingresó código", "instrucciones": [], "tokens": []}

    errores = [i for i in instrucciones if not i["exito"]]
    return {
        "exito": not errores,
        "error": f"Línea {errores[0]['linea']}: {errores[0]['error']}" if errores else None,
        "instrucciones": instrucciones,
        "tokens": [token for i in instrucciones for token in i["tokens"]],
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # En producción acotarlo a "http://localhost"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Interfaz web (src/ui) servida por el mismo backend en /ui/.
# La usan tanto la app de escritorio (app.py) como el despliegue en línea (Docker/Render).
RUTA_UI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui")
app.mount("/ui", StaticFiles(directory=RUTA_UI, html=True), name="ui")
