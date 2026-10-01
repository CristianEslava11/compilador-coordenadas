from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel

from AnalisiLexicoCoordenadas import tokenizar
from AnalisisSintactico import parser

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="GeoQuery", description="API para ejecutar el programa de lenguaje de coordenadas", version="1.0.0")


class CodigoRequest(BaseModel):
	codigo: str



@app.get("/")
def inicio():
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # En producción acotarlo a "http://localhost"
    allow_methods=["*"],
    allow_headers=["*"],
)

