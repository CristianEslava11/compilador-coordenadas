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


@app.post("/iniciar")
def ejecutar_codigo(request: CodigoRequest):
    try:
        codigo = request.codigo.strip()
        if not codigo:
            return {"exito": False, "error": "No se ingresó código"}
        tokens = tokenizar(codigo)
        analizador = parser(tokens)
        resultado = analizador.analizador()
        if analizador.pos != len(tokens):
            return {
                "exito": False,
                "error": "La consulta contiene tokens adicionales no válidos"
            }

        return {
            "exito": True,
            "resultado": resultado,
            "tokens": [token.to_json() for token in tokens]
        }

    except (SyntaxError, ValueError) as error:
        return {
            "exito": False,
            "error": str(error)
        }
    except Exception as error:
        return {
            "exito": False,
            "error": f"Error interno: {str(error)}"
        }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # En producción acotarlo a "http://localhost"
    allow_methods=["*"],
    allow_headers=["*"],
)

