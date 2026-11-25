# Orquesta las fases del compilador GeoQuery para un programa .geo:
#   léxico -> sintáctico -> semántico -> ejecución
# Un programa tiene una instrucción por línea; las líneas vacías y las que
# empiezan con # (comentarios) se ignoran.

from AnalisiLexicoCoordenadas import tokenizar
from AnalisisSintactico import parser
from AnalisisSemantico import ErrorSemantico, analizar as analizar_semantica
from Ejecucion import CONSULTAN_SERVICIO, ErrorEjecucion, ejecutar
from ServicioGeografico import ErrorServicioGeografico

# Máximo de instrucciones por programa que consultan OpenStreetMap (COORDENADA y
# UBICACION), para no abusar del servicio: cada consulta tarda al menos 1 segundo.
MAX_CONSULTAS_SERVICIO = 15


def compilar_instruccion(texto, num_linea, permitir_consulta=True):
    """Pasa una instrucción por todas las fases. "fase" indica en qué etapa
    ocurrió el error: lexico, sintactico, semantico, ejecucion o interno."""
    fase = "lexico"
    tokens = []
    salida = {"linea": num_linea, "codigo": texto}
    try:
        tokens = tokenizar(texto)

        fase = "sintactico"
        analizador = parser(tokens)
        resultado = analizador.analizador()
        if analizador.pos != len(tokens):
            raise SyntaxError("La instrucción contiene tokens adicionales no válidos")
        salida["resultado"] = resultado

        fase = "semantico"
        analizar_semantica(resultado)

        fase = "ejecucion"
        if resultado["comando"] in CONSULTAN_SERVICIO and not permitir_consulta:
            raise ErrorEjecucion(
                f"Se alcanzó el límite de {MAX_CONSULTAS_SERVICIO} consultas de lugares por programa")
        salida["salida"] = ejecutar(resultado)
        salida["exito"] = True

    except (SyntaxError, ValueError, ErrorSemantico, ErrorEjecucion, ErrorServicioGeografico) as error:
        salida.update(exito=False, fase=fase, error=str(error))
    except Exception as error:
        salida.update(exito=False, fase="interno", error=f"Error interno: {error}")

    salida["tokens"] = [{**token.to_json(), "linea": num_linea} for token in tokens]
    return salida


def compilar_programa(codigo):
    """Compila un programa completo y devuelve la lista de instrucciones analizadas."""
    instrucciones = []
    consultas = 0
    for num_linea, linea in enumerate(codigo.splitlines(), start=1):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        consulta = linea.split("(", 1)[0].strip().lower() in CONSULTAN_SERVICIO
        if consulta:
            consultas += 1
        instrucciones.append(
            compilar_instruccion(linea, num_linea, permitir_consulta=consultas <= MAX_CONSULTAS_SERVICIO))
    return instrucciones
