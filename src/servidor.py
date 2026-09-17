import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, List, Optional

# Asegurar que Python encuentre los módulos en la misma carpeta 'src'
DIR_SRC = os.path.dirname(os.path.abspath(__file__))
if DIR_SRC not in sys.path:
    sys.path.insert(0, DIR_SRC)

from AnalisiLexicoCoordenadas import tokenizar
from AnalisisSintactico import parser

# Inicialización de la aplicación FastAPI
app = FastAPI(
    title="GeoQuery API - Compilador de Coordenadas",
    description="API REST para análisis léxico y sintáctico del lenguaje GeoQuery (.geo)",
    version="1.0.0"
)

# Modelo de datos de entrada esperado según la guía
class CodigoEntrada(BaseModel):
    codigo: str

# Modelo de datos para representar cada Token en la respuesta
class TokenResponse(BaseModel):
    tipo: str
    valor: Any

# Modelo de respuesta general
class CompiladorResponse(BaseModel):
    exito: bool
    resultado: Optional[Any] = None
    tokens: List[TokenResponse] = []
    error: Optional[str] = None


@app.get("/", summary="Información del Lenguaje")
def ruta_raiz():
    """Endpoint informativo de bienvenida con detalles del lenguaje."""
    return {
        "lenguaje": "GeoQuery",
        "extension": ".geo",
        "version": "1.0.0",
        "descripcion": "Compilador y lenguaje para consultas de coordenadas geográficas",
        "comandos_soportados": [
            "COORDENADA(latitud, longitud)",
            "VALIDAR(latitud, longitud)",
            "UBICACION('nombre_lugar')",
            "DISTANCIA(lat1, lon1, lat2, lon2)",
            "HEMISFERIO(latitud, longitud)"
        ],
        "documentacion_swagger": "/docs"
    }


@app.post("/iniciar", response_model=CompiladorResponse, summary="Compilar código GeoQuery")
def iniciar_compilacion(entrada: CodigoEntrada):
    """
    Recibe una instrucción en código fuente GeoQuery, ejecuta el análisis
    léxico y sintáctico, y retorna los tokens junto al resultado o los errores encontrados.
    """
    codigo = entrada.codigo.strip()
    if not codigo:
        raise HTTPException(status_code=400, detail="El código fuente no puede estar vacío.")

    tokens_procesados = []
    
    # 1. Análisis Léxico
    try:
        tokens = tokenizar(codigo)
        tokens_procesados = [{"tipo": t.tipo, "valor": t.valor} for t in tokens]
    except ValueError as error_lexico:
        return CompiladorResponse(
            exito=False,
            error=f"Error léxico: {error_lexico}",
            tokens=tokens_procesados,
            resultado=None
        )

    # 2. Análisis Sintáctico
    try:
        analizador = parser(tokens)
        resultado = analizador.analizador()
        return CompiladorResponse(
            exito=True,
            resultado=resultado,
            tokens=tokens_procesados,
            error=None
        )
    except SyntaxError as error_sintactico:
        return CompiladorResponse(
            exito=False,
            error=f"Error sintáctico: {error_sintactico}",
            tokens=tokens_procesados,
            resultado=None
        )
    except Exception as error_interno:
        return CompiladorResponse(
            exito=False,
            error=f"Error interno del compilador: {str(error_interno)}",
            tokens=tokens_procesados,
            resultado=None
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("servidor:app", host="0.0.0.0", port=8000, reload=True)
