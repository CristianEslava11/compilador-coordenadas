# Ejecución (intérprete): recibe una instrucción ya validada por el análisis
# semántico y calcula su resultado.

import math

import ServicioGeografico
from AnalisisSemantico import errores_de_rango

RADIO_TIERRA_KM = 6371.0088   # radio medio de la Tierra (IUGG)


class ErrorEjecucion(Exception):
    pass


def ejecutar_coordenada(argumentos):
    latitud, longitud = argumentos
    return {
        "latitud": latitud,
        "longitud": longitud,
        "lugar": ServicioGeografico.lugar_de_coordenada(latitud, longitud),
        "fuente": ServicioGeografico.ATRIBUCION,
    }


def ejecutar_validar(argumentos):
    motivos = errores_de_rango(*argumentos)
    return {"valida": not motivos, "motivos": motivos}


def haversine(latitud1, longitud1, latitud2, longitud2):
    """Distancia del círculo máximo entre dos puntos de la esfera terrestre, en km."""
    phi1, phi2 = math.radians(latitud1), math.radians(latitud2)
    delta_phi = math.radians(latitud2 - latitud1)
    delta_lambda = math.radians(longitud2 - longitud1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    return 2 * RADIO_TIERRA_KM * math.asin(math.sqrt(a))


def ejecutar_distancia(argumentos):
    (latitud1, longitud1), (latitud2, longitud2) = argumentos
    return {"kilometros": round(haversine(latitud1, longitud1, latitud2, longitud2), 2)}


def ejecutar_hemisferio(argumentos):
    latitud, longitud = argumentos

    if latitud > 0:
        latitudinal = "Norte"
    elif latitud < 0:
        latitudinal = "Sur"
    else:
        latitudinal = "Ecuador (límite entre Norte y Sur)"

    if abs(longitud) == 180:
        longitudinal = "Antimeridiano (límite entre Este y Oeste)"
    elif longitud > 0:
        longitudinal = "Este"
    elif longitud < 0:
        longitudinal = "Oeste"
    else:
        longitudinal = "Meridiano de Greenwich (límite entre Este y Oeste)"

    return {"latitudinal": latitudinal, "longitudinal": longitudinal}


def ejecutar_ubicacion(nombre):
    lugar = ServicioGeografico.buscar_lugar(nombre)
    if lugar is None:
        raise ErrorEjecucion(f"No se encontró ningún lugar llamado '{nombre}'")
    return {**lugar, "fuente": ServicioGeografico.ATRIBUCION}


ACCIONES = {
    "coordenada": ejecutar_coordenada,
    "validar": ejecutar_validar,
    "distancia": ejecutar_distancia,
    "hemisferio": ejecutar_hemisferio,
    "ubicacion": ejecutar_ubicacion,
}

# Instrucciones que consultan el servicio de ubicaciones (OpenStreetMap)
CONSULTAN_SERVICIO = {"coordenada", "ubicacion"}


def ejecutar(resultado):
    """Recibe el AST ({"comando", "argumentos"}) y devuelve el resultado de la instrucción."""
    accion = ACCIONES.get(resultado["comando"])
    if accion is None:
        raise ErrorEjecucion(f"La instrucción '{resultado['comando']}' no se puede ejecutar")
    return accion(resultado["argumentos"])
