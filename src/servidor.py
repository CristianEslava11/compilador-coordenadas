import os

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
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


INFO = {"lenguaje":"GEO",
		"version":"1.0.0",
		"estado":"en desarrollo",
		"datos_geograficos":"© OpenStreetMap contributors (Nominatim)"}


@app.get("/")
def inicio(request: Request):
	# Un navegador que entra a la raíz se envía a la interfaz; un cliente de la API
	# (curl, fetch, health checks) recibe el JSON de estado.
	if "text/html" in request.headers.get("accept", ""):
		return RedirectResponse("/ui/")
	return INFO


@app.get("/info")
def info():
	return INFO


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

# Orígenes permitidos: variable CORS_ORIGINS separada por comas (por defecto "*").
# La UI desplegada se sirve desde el mismo origen, así que no depende de esto.
ORIGENES = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Interfaz web (src/ui) servida por el mismo backend en /ui/.
# La usan tanto la app de escritorio (app.py) como el despliegue en línea (Docker/Render).
# En el .exe de PyInstaller, __file__ apunta a la carpeta donde se extraen los archivos.
RUTA_UI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui")
app.mount("/ui", StaticFiles(directory=RUTA_UI, html=True), name="ui")
