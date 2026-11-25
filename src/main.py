import sys
import os

from Compilador import compilar_instruccion, compilar_programa

EXTENSION = ".geo"

NOMBRE_FASE = {
    "lexico": "Error léxico",
    "sintactico": "Error sintáctico",
    "semantico": "Error semántico",
    "ejecucion": "Error de ejecución",
    "interno": "Error interno",
}


def describir_salida(instruccion):
    """Texto con el resultado de una instrucción ya ejecutada."""
    comando = instruccion["resultado"]["comando"]
    salida = instruccion["salida"]
    if comando == "coordenada":
        return salida["lugar"] or "Sin lugar asociado (océano o zona sin datos)"
    if comando == "validar":
        return "Coordenada válida" if salida["valida"] else "Coordenada inválida: " + "; ".join(salida["motivos"])
    if comando == "distancia":
        return f"{salida['kilometros']} km"
    if comando == "hemisferio":
        return f"{salida['latitudinal']} · {salida['longitudinal']}"
    if comando == "ubicacion":
        return f"{salida['nombre']} ({salida['latitud']:.4f}, {salida['longitud']:.4f})"
    return str(salida)


def mostrar_instruccion(instruccion):
    print("Tokens:", [f"{t['tipo']}:{t['valor']}" for t in instruccion["tokens"]])
    if instruccion.get("resultado"):
        print("Árbol:", instruccion["resultado"])
    if instruccion["exito"]:
        print("Resultado:", describir_salida(instruccion))
    else:
        print(f"{NOMBRE_FASE.get(instruccion['fase'], 'Error')}: {instruccion['error']}")


def ejecutar_linea(texto):
    texto = texto.strip()

    if not texto:
        return True

    instruccion = compilar_instruccion(texto, 1)
    mostrar_instruccion(instruccion)
    return instruccion

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
    # Misma regla que la interfaz: una instrucción por línea, # para comentarios
    for instruccion in compilar_programa(contenido):
        print(f"\n--- Línea {instruccion['linea']}: {instruccion['codigo']} ---")
        mostrar_instruccion(instruccion)
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
    print("  python main.py                  modo interactivo (GEO>)")
    print(f"  python main.py archivo{EXTENSION}     ejecuta un programa (una instrucción por línea, # comentarios)")
    print("Instrucciones:")
    print("  COORDENADA(latitud, longitud)         lugar en esa coordenada")
    print("  VALIDAR(latitud, longitud)            indica si la coordenada es válida")
    print("  DISTANCIA(lat1, lon1), (lat2, lon2)   distancia en km entre dos puntos")
    print("  HEMISFERIO(latitud, longitud)         hemisferios de la coordenada")
    print("  UBICACION('lugar')                    coordenadas de un lugar")
    print("Escribe CERRAR para salir del modo interactivo")
    print("Datos de lugares: © OpenStreetMap contributors (Nominatim)")

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
