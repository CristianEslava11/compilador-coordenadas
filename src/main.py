from AnalisiLexicoCoordenadas import tokenizar
from AnalisisSintactico import parser

if __name__ == "__main__":
    expresion = input("Ingrese la información: ")
    
    try:
        # 1. Análisis Léxico
        tokens = tokenizar(expresion)
        print("Tokens generados:", tokens)

        # 2. Análisis Sintáctico
        analizador_sintactico = parser(tokens)
        resultado = analizador_sintactico.analizador()
        print("Resultado del análisis sintáctico:", resultado)
        
    except (SyntaxError, ValueError) as e:
        print(f"Error: {e}")
