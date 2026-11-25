# Análisis semántico: verifica que los valores de una instrucción ya reconocida por el
# parser tengan sentido geográfico (latitud entre -90 y 90, longitud entre -180 y 180).

LATITUD_MIN, LATITUD_MAX = -90.0, 90.0
LONGITUD_MIN, LONGITUD_MAX = -180.0, 180.0


class ErrorSemantico(Exception):
    pass


def formatear(numero):
    # 95.0 -> "95", 4.711 -> "4.711"
    return f"{numero:g}"


def errores_de_rango(latitud, longitud):
    """Devuelve la lista de problemas de una coordenada (vacía si es válida)."""
    errores = []
    if not LATITUD_MIN <= latitud <= LATITUD_MAX:
        errores.append(f"latitud {formatear(latitud)} fuera de rango (debe estar entre -90 y 90)")
    if not LONGITUD_MIN <= longitud <= LONGITUD_MAX:
        errores.append(f"longitud {formatear(longitud)} fuera de rango (debe estar entre -180 y 180)")
    return errores


def verificar_coordenada(coordenada, nombre=None):
    errores = errores_de_rango(*coordenada)
    if errores:
        prefijo = f"En el {nombre}: " if nombre else ""
        mensaje = "; ".join(errores)
        raise ErrorSemantico(prefijo + mensaje[0].upper() + mensaje[1:])


def regla_una_coordenada(argumentos):
    verificar_coordenada(argumentos)


def regla_distancia(argumentos):
    verificar_coordenada(argumentos[0], "punto A")
    verificar_coordenada(argumentos[1], "punto B")


def sin_verificacion(argumentos):
    # VALIDAR no falla: su resultado es justamente decir si la coordenada es válida.
    # UBICACION recibe un nombre, no números.
    pass


REGLAS_SEMANTICAS = {
    "coordenada": regla_una_coordenada,
    "hemisferio": regla_una_coordenada,
    "distancia": regla_distancia,
    "validar": sin_verificacion,
    "ubicacion": sin_verificacion,
}


def analizar(resultado):
    """Recibe el AST del parser ({"comando", "argumentos"}) y lanza ErrorSemantico
    si los valores no son válidos. Si todo está bien, devuelve el mismo AST."""
    regla = REGLAS_SEMANTICAS.get(resultado["comando"])
    if regla is None:
        raise ErrorSemantico(f"No hay reglas semánticas para '{resultado['comando']}'")
    regla(resultado["argumentos"])
    return resultado
