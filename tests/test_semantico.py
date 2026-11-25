import pytest

from AnalisisSemantico import ErrorSemantico, analizar, errores_de_rango


@pytest.mark.parametrize("latitud, longitud", [
    (0, 0), (90, 180), (-90, -180), (4.711, -74.0721),
])
def test_coordenadas_en_rango(latitud, longitud):
    assert errores_de_rango(latitud, longitud) == []


def test_latitud_y_longitud_fuera_de_rango():
    errores = errores_de_rango(95, -200)
    assert len(errores) == 2
    assert "latitud 95" in errores[0]
    assert "longitud -200" in errores[1]


@pytest.mark.parametrize("comando", ["coordenada", "hemisferio"])
def test_coordenada_invalida_es_error_semantico(comando):
    with pytest.raises(ErrorSemantico, match="Latitud 90.5 fuera de rango"):
        analizar({"comando": comando, "argumentos": (90.5, 0)})


def test_distancia_indica_el_punto_invalido():
    with pytest.raises(ErrorSemantico, match="punto B: Latitud 91"):
        analizar({"comando": "distancia", "argumentos": ((4, -74), (91, 10))})


def test_validar_nunca_falla():
    # VALIDAR informa la validez en la ejecución; no es un error semántico
    ast = {"comando": "validar", "argumentos": (95, -200)}
    assert analizar(ast) is ast


def test_ubicacion_no_tiene_restricciones_numericas():
    ast = {"comando": "ubicacion", "argumentos": "Tunja"}
    assert analizar(ast) is ast
