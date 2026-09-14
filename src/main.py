import subprocess
import sys
import os

from AnalisiLexicoCoordenadas import tokenizar
from AnalisisSintactico import parser

EXTENSION = ".geo"

def ejecutar_linea(texto):
    texto = texto.strip()

    if not texto:
        return True

    try:
        tokens = tokenizar(texto)
        print("Tokens:", tokens)

        analizador = parser(tokens)
        resultado = analizador.analizador()
        print("Resultado:", resultado)
        return resultado
    except (SyntaxError, ValueError) as error:
        print(f"Error de sintaxis/léxico: {error}")
        return True

def ejecutar_archivos(ruta):

    if not os.path.exists(ruta):
        print(f"Error: el archivo '{ruta}' no existe.")
        return False
    
    if not ruta.lower().endswith(EXTENSION):
        print(f"Error: el archivo debe tener la extension {EXTENSION}")
        return False
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            contenido = archivo.read()
    except Exception as error:
        print(f"Error leyendo el archivo: {error}")
        return False
    if not contenido.strip():
        print("El archivo está vacío.")
        return False

    print(f"Procesando archivo: {ruta}")
    lineas = contenido.splitlines()
    for num_linea, linea in enumerate(lineas, start=1):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        print(f"\n--- Línea {num_linea}: {linea} ---")
        ejecutar_linea(linea)
    return True

def modo_interactivo():

    print("BIENVENIDO A GEOQUERY")
    print("Escribe el comando que deseas ejecutar")
    print("Escribe CERRAR para salir")

    while True:

        try:
            texto = input("GEO> ")
        except KeyboardInterrupt:
            print("Programa terminado")
            break
        except EOFError:
            print("Programa terminado")
            break

        texto_limpio = texto.strip()
        if texto_limpio.upper() in ["CERRAR", "SALIR", "EXIT"]:
            print("Programa terminado. ¡Hasta luego!")
            break

        if not texto_limpio:
            continue

        resultado = ejecutar_linea(texto_limpio)

def mostrar_ayuda():

    print("GeoQuery Language")
    print("Uso:")
    print("COORDENADA (latitud, longitud)")
    print("VALIDAR (latitud, longitud)")
    print("UBICACION (latitud, longitud)")
    print("DISTANCIA (latitud1, longitud1, latitud2, longitud2)")
    print("HEMISFERIO (latitud, longitud)")
    print("CERRAR para salir")
    print(f"Extension soportada: {EXTENSION}")

def main():

    if len(sys.argv) == 1:
        modo_interactivo()
        return

    if (sys.argv[1] == "--help" or sys.argv[1] == "-h"):
        mostrar_ayuda()
        return

    if len(sys.argv) == 2:
        ruta = sys.argv[1]
        ejecutar_archivos(ruta)
        return

    print("Error: cantidad de argumentos")

    mostrar_ayuda()

if __name__ == "__main__":
    main()
