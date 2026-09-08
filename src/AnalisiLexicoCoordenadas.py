from Token import Token
import re


def tokenizar(texto):
    tokens = []
    i = 0
    simbolos = {
        "(" : "LPARENT",
        ")" : "RPARENT",
        "," : "COMA",
        "'" : "COMILLA"
    }

    palabrasClave = ["coordenada", "ubicacion", "distancia", "hemisferio", "validar"]

    while i < len(texto):
        char = texto[i]
        n = len(texto)

        if char.isspace():
            i += 1
            continue    

        if char.isalpha():
            inicio = i
            while i < n and texto[i].isalpha():
                i += 1
            palabra = texto[inicio:i]

            if palabra in palabrasClave:
                tokens.append(Token("IDENTIFICADOR", palabra))
            else:
                tokens.append(Token("STRING", palabra))
            continue

        if char in simbolos:
            tokens.append(Token(simbolos[char], char))
            i = i+1
            continue


        if char.isdigit() or (char == "-" and texto[i + 1].isdigit()):
            inicio = i
            tipo_numero = "NUMERO"
            if char == "-":
                i += 1
                tipo_numero = "NEGATIVO"
            while i < n and (texto[i].isdigit() or texto[i] == "."):
                i += 1
            tokens.append(Token(tipo_numero, float(texto[inicio:i])))
            continue

        raise ValueError(f"Carácter no reconocido: {char!r}")

    return tokens
