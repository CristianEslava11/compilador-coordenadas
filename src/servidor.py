import os
import sys

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from AnalisiLexicoCoordenadas import tokenizar
from AnalisisSintactico import parser

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="GeoQuery", description="API para ejecutar el programa de lenguaje de coordenadas", version="1.0.0")


class CodigoRequest(BaseModel):
	codigo: str



# Carpeta base: dentro del .exe de PyInstaller los archivos se extraen en sys._MEIPASS
BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


@app.get("/")
def inicio(request: Request):
	# Un navegador que entra a la raíz se envía a la interfaz; el fetch() de la UI
	# (Accept: */*) sigue recibiendo el JSON de estado.
	if "text/html" in request.headers.get("accept", ""):
		return RedirectResponse("/ui/")
	return {"lenguaje":"GEO",
			"version":"1.0.0",
			"estado":"en desarrollo"}


def analizar_instruccion(texto, num_linea):
    """Analiza una sola instrucción (una línea) y devuelve su resultado.
    "fase" indica en qué etapa del compilador ocurrió el error (lexico, sintactico, interno)."""
    fase = "lexico"
    tokens = []
    salida = {"linea": num_linea, "codigo": texto}
    try:
        tokens = tokenizar(texto)

        fase = "sintactico"
        analizador = parser(tokens)
        resultado = analizador.analizador()
        if analizador.pos != len(tokens):
            raise SyntaxError("La instrucción contiene tokens adicionales no válidos")

        salida.update(exito=True, resultado=resultado)
    except (SyntaxError, ValueError) as error:
        salida.update(exito=False, fase=fase, error=str(error))
    except Exception as error:
        salida.update(exito=False, fase="interno", error=f"Error interno: {error}")

    salida["tokens"] = [{**token.to_json(), "linea": num_linea} for token in tokens]
    return salida


@app.post("/iniciar")
def ejecutar_codigo(request: CodigoRequest):
    # Una instrucción por línea; se ignoran las líneas vacías y los comentarios (#),
    # igual que en el modo archivo del CLI (main.py)
    instrucciones = [
        analizar_instruccion(linea.strip(), num_linea)
        for num_linea, linea in enumerate(request.codigo.splitlines(), start=1)
        if linea.strip() and not linea.strip().startswith("#")
    ]

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

# La UI se sirve desde el mismo servidor que la API (/ui/), tanto en la web/Docker
# como en la app de escritorio (app.py importa esta misma app).
app.mount("/ui", StaticFiles(directory=os.path.join(BASE, "ui"), html=True), name="ui")
