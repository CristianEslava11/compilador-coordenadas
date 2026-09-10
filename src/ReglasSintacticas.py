import json
import os


PALABRAS_CLAVE = ["coordenada", "ubicacion", "distancia", "hemisferio", "validar"]

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
        raise SyntaxError("Error Sintáctico: Se esperaba '[]' al inicio de la coordenada")
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
        raise SyntaxError("Error Sintáctico: Se esperaba ']' al final de la coordenada")
    parser.pos += 1

    return (latitud, longitud)


def regla_distancia(parser):
    coordenada_1 = revisar_validacion_coordenada(parser)
    if parser.pos >= len(parser.tokens) or parser.tokens[parser.pos].tipo != "COMA":
        raise SyntaxError("Error Sintáctico: Se esperaba ',' entre las coordenadas")
    parser.pos += 1
    coordenada_2 = revisar_validacion_coordenada(parser)
    return (coordenada_1, coordenada_2)

def regla_ubicacion(parser):
    if parser.pos >= len(parser.tokens) or parser.tokens[parser.pos].tipo != "LPARENT":
        raise SyntaxError("Error Sintáctico: Se esperaba '[' al inicio de la coordenada")
    parser.pos += 1

    if parser.pos >= len(parser.tokens) or parser.tokens[parser.pos].tipo != "COMILLA":
        raise SyntaxError("Error Sintáctico: Se esperaba ''' al inicio de la coordenada")
    parser.pos += 1

    if parser.pos >= len(parser.tokens) or parser.tokens[parser.pos].tipo not in ["STRING"]:
        raise SyntaxError("Error Sintáctico: Se esperaba un STRING para la ubicación")
    nombre_ubicacion = parser.tokens[parser.pos].valor
    parser.pos += 1

    if parser.pos >= len(parser.tokens) or parser.tokens[parser.pos].tipo != "COMILLA":
        raise SyntaxError("Error Sintáctico: Se esperaba ''' al final de la coordenada")
    parser.pos += 1

    if parser.pos >= len(parser.tokens) or parser.tokens[parser.pos].tipo != "RPARENT":
        raise SyntaxError("Error Sintáctico: Se esperaba ']' al final de la coordenada")
    parser.pos += 1

    return nombre_ubicacion

