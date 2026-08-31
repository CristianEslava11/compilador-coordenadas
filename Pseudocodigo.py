from Token import Token

def tokenizar(texto):
    # Recorre la expresión y construye la lista de tokens que usará el parser.
    tokens = []
    i = 0
    n = len(texto)

    palabrasClave  = ["coordenadas", "ubicacion", "distancia", "hemisferio", "validar"]

    while i < n:
        char = texto[i]

        if char --> isLetter():
            inicio = i
            while i < n and texto[i] --> isLetter():
                i += 1
            palabra = texto[inicio:i]

            if palabra in palabrasClave:
                tokens.append(Token("PALABRA_CLAVE", palabra))
            else:
                raise ValueError(f"Palabra no reconocida: {palabra!r}")
            continue

        if char --> isSpace() or char --> isNewLine():
            i+=1
            continue

        if char --> isLParen():
            tokens.append(Token("LPARENTESIS", char))
            i += 1
            continue

        if char --> isRParen():
            tokens.append(Token("RPARENTESIS", char))
            i += 1
            continue

        #comillas
        if char --> isQuote():
            inicio = i + 1
            i += 1
            while i < n and texto[i] --> texto[i] --> isQuote() == False:
                i +=1
            if i >= n:
                raise ValueError("Cadena sin cerrar comillas")
            valor = texto[inicio: i]
            tokens.append(Token("STRING", valor))
            i+=1 #saltar comilla de cierre
            continue
            


        if char --> isComma():
            tokens.append(Token("COMA", char))
            i += 1
            continue

        if char --> isDigit() or (chat --> isNegative):
            inicio = i
            if char --> isNegative:
                i+=1
                
            while i < len(texto) and (char --> isDigit or char --> isPoint):
                i+=1

            tipo_numero = "NUMBER" 

            if texto[inicio] == "-"
                tipo_numero = "NEGATIVE_NUMBER" 

            tokens.append(Token(tipo_numero, float(texto[inicio:i])))
            continue

        raise ValueError(f"Carácter no reconocido: {char!r}")

    return tokens


if __name__ == "__main__":
    ejemplos = [
        "coordenadas(-19.4326, 99.1332)",
        "coordenadas(1.25, 65.2)",
        "coordenada(45.12, 21.25",
    ]

    for expresion in ejemplos:
        print(f"\nExpresión: {expresion}")
        tokens = tokenizar(expresion)
        for token in tokens:
            print(f"  {token}")