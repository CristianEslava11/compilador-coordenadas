

import json
import os

def cargar_palabras_clave_desde_json():
    ruta_json = os.path.join(os.path.dirname(__file__), "persistencia", "reglas.json")
    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            datos = json.load(f)
            regla_1 = datos[0].get("Regla_1", {})
            palabras = regla_1.get("revisar_palabra_clave", [])
            if palabras:
                return palabras
    except Exception:
        pass
    return ["coordenada", "ubicacion", "distancia", "hemisferio", "validar"]


PALABRAS_CLAVE = cargar_palabras_clave_desde_json()

# El parser es un objeto que contiene la lista de tokens y la posicion actual del parser
def revisar_palabra_clave(parser):
    # Verificamos si el parser llegó al final de la lista de tokens
    if parser.pos >= len(parser.tokens):
        raise SyntaxError("Error: No se encontró la palabra clave al inicio")

    token_actual = parser.tokens[parser.pos]


    if token_actual.tipo == "IDENTIFICADOR" and token_actual.valor in PALABRAS_CLAVE:
        comando = token_actual.valor
        parser.pos += 1
        return comando
    else:
        raise SyntaxError("Error: No se encontró una palabra clave válida al inicio")

def revisar_validacion_coordenada(parser):
    if parser.pos >= len(parser.tokens) or parser.tokens[parser.pos].tipo != "LPARENT":
        raise SyntaxError("Error Sintáctico: Se esperaba '(' al inicio de la coordenada")
    parser.pos += 1

    if parser.pos >= len(parser.tokens) or parser.tokens[parser.pos].tipo not in ["NUMERO", "NEGATIVO"]:
        raise SyntaxError("Error Sintáctico: Se esperaba un número para la latitud")
    latitud = parser.tokens[parser.pos].valor
    parser.pos += 1

    if parser.pos >= len(parser.tokens) or parser.tokens[parser.pos].tipo != "COMA":
        raise SyntaxError("Error Sintáctico: Se esperaba ',' entre latitud y longitud")
    parser.pos += 1

    if parser.pos >= len(parser.tokens) or parser.tokens[parser.pos].tipo not in ["NUMERO", "NEGATIVO"]:
        raise SyntaxError("Error Sintáctico: Se esperaba un número para la longitud")
    longitud = parser.tokens[parser.pos].valor
    parser.pos += 1

    if parser.pos >= len(parser.tokens) or parser.tokens[parser.pos].tipo != "RPARENT":
        raise SyntaxError("Error Sintáctico: Se esperaba ')' al final de la coordenada")
    parser.pos += 1

    return (latitud, longitud)



            
            

        
    
