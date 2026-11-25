from Token import Token


def tokenizar(texto):
    tokens = []
    i = 0
    n = len(texto)
    simbolos = {
        "(" : "LPARENT",
        ")" : "RPARENT",
        "," : "COMA",
    }

    palabrasClave = ["coordenada", "ubicacion", "distancia", "hemisferio", "validar"]

    while i < n:
        char = texto[i]

        if char.isspace():
            i += 1
            continue

        if char.isalpha():
            inicio = i
            while i < n and texto[i].isalpha():
                i += 1
            palabra = texto[inicio:i]

            if palabra.lower() in palabrasClave:
                tokens.append(Token("IDENTIFICADOR", palabra.lower()))
            else:
                tokens.append(Token("STRING", palabra))
            continue

        # Cadena entre comillas: todo lo que hay hasta la comilla de cierre es un solo
        # STRING, así se aceptan nombres con espacios o puntos ('San Andrés', 'Bogotá D.C.')
        if char == "'":
            tokens.append(Token("COMILLA", char))
            cierre = texto.find("'", i + 1)
            if cierre == -1:
                raise ValueError("Cadena sin cerrar: falta la comilla (') de cierre")
            contenido = texto[i + 1:cierre].strip()
            if contenido:
                tokens.append(Token("STRING", contenido))
            tokens.append(Token("COMILLA", "'"))
            i = cierre + 1
            continue

        if char in simbolos:
            tokens.append(Token(simbolos[char], char))
            i = i+1
            continue

        if char.isdigit() or (
            char == "-" and i + 1 < n and texto[i + 1].isdigit()
        ):
            inicio = i
            tipo_numero = "NUMERO"
            if char == "-":
                i += 1
                tipo_numero = "NEGATIVO"
            while i < n and (texto[i].isdigit() or texto[i] == "."):
                i += 1
            lexema = texto[inicio:i]
            tokens.append(Token(tipo_numero, convertir_numero(lexema)))
            continue

        # Un punto seguido de dígitos (".5") es un número sin la parte entera
        if char == "." and i + 1 < n and texto[i + 1].isdigit():
            raise ValueError(f"Número mal formado: '{texto[i:i + 2]}…' (escribe 0{texto[i:i + 2]}…)")

        raise ValueError(f"Carácter no reconocido: {char!r}")

    return tokens


def convertir_numero(lexema):
    """Un número válido es: dígitos, opcionalmente seguidos de un punto y más dígitos
    (ej. 4, 4.7110, -74.0721). Rechaza formas como '4.7.1' o '4.'."""
    sin_signo = lexema.lstrip("-")
    entero, punto, decimales = sin_signo.partition(".")
    if not entero.isdigit() or (punto and not decimales.isdigit()):
        raise ValueError(f"Número mal formado: '{lexema}'")
    return float(lexema)
