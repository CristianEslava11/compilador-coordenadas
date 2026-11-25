import pytest

from AnalisiLexicoCoordenadas import tokenizar
from AnalisisSintactico import parser


def analizar(texto):
    analizador = parser(tokenizar(texto))
    resultado = analizador.analizador()
    return resultado, analizador


@pytest.mark.parametrize("comando", ["coordenada", "validar", "hemisferio"])
def test_instrucciones_de_una_coordenada(comando):
    resultado, analizador = analizar(f"{comando}(4.7110, -74.0721)")
    assert resultado == {"comando": comando, "argumentos": (4.711, -74.0721)}
    assert analizador.pos == len(analizador.tokens)


def test_distancia():
    resultado, _ = analizar("distancia(4.7110, -74.0721), (6.2442, -75.5812)")
    assert resultado == {"comando": "distancia", "argumentos": ((4.711, -74.0721), (6.2442, -75.5812))}


def test_ubicacion():
    resultado, _ = analizar("ubicacion('San Andrés')")
    assert resultado == {"comando": "ubicacion", "argumentos": "San Andrés"}


@pytest.mark.parametrize("texto, mensaje", [
    ("coordenada 4, 5", r"Se esperaba '\('"),
    ("coordenada(, 5)", "número para la latitud"),
    ("coordenada(4 5)", "Se esperaba ','"),
    ("coordenada(4, )", "número para la longitud"),
    ("coordenada(4, 5", r"Se esperaba '\)'"),
    ("distancia(1, 2) (3, 4)", "entre las coordenadas"),
    ("ubicacion(Tunja)", "entre comillas simples"),
    ("ubicacion('')", "nombre del lugar"),
    ("ubicacion('Tunja'", r"Se esperaba '\)' al final de UBICACION"),
])
def test_errores_sintacticos(texto, mensaje):
    with pytest.raises(SyntaxError, match=mensaje):
        analizar(texto)


def test_instruccion_desconocida_lista_las_validas():
    with pytest.raises(SyntaxError, match="Instrucción desconocida 'validacion'.*VALIDAR"):
        analizar("validacion(1, 2)")


def test_linea_que_no_empieza_con_instruccion():
    with pytest.raises(SyntaxError, match="debe comenzar con una instrucción"):
        analizar("(1, 2)")


def test_tokens_sobrantes_no_se_consumen():
    # El parser se detiene al terminar la instrucción; el compilador reporta los sobrantes
    _, analizador = analizar("coordenada(1, 2) validar(3, 4)")
    assert analizador.pos < len(analizador.tokens)
