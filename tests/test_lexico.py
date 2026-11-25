import pytest

from AnalisiLexicoCoordenadas import tokenizar


def tipos_y_valores(texto):
    return [(t.tipo, t.valor) for t in tokenizar(texto)]


def test_coordenada_completa():
    assert tipos_y_valores("coordenada(4.7110, -74.0721)") == [
        ("IDENTIFICADOR", "coordenada"),
        ("LPARENT", "("),
        ("NUMERO", 4.711),
        ("COMA", ","),
        ("NEGATIVO", -74.0721),
        ("RPARENT", ")"),
    ]


def test_palabras_clave_sin_distinguir_mayusculas():
    for texto in ["COORDENADA", "Coordenada", "coordenada"]:
        assert tipos_y_valores(texto) == [("IDENTIFICADOR", "coordenada")]


def test_palabra_que_no_es_clave_es_string():
    assert tipos_y_valores("validacion") == [("STRING", "validacion")]


def test_numeros_enteros_y_decimales():
    assert tipos_y_valores("4 -74 0.5") == [("NUMERO", 4.0), ("NEGATIVO", -74.0), ("NUMERO", 0.5)]


def test_espacios_y_saltos_se_ignoran():
    assert tipos_y_valores("  validar ( 1 ,\t2 )  ") == tipos_y_valores("validar(1,2)")


def test_cadena_con_espacios_y_puntos():
    assert tipos_y_valores("ubicacion('Bogotá D.C.')") == [
        ("IDENTIFICADOR", "ubicacion"),
        ("LPARENT", "("),
        ("COMILLA", "'"),
        ("STRING", "Bogotá D.C."),
        ("COMILLA", "'"),
        ("RPARENT", ")"),
    ]


def test_cadena_vacia_no_genera_string():
    assert [t.tipo for t in tokenizar("''")] == ["COMILLA", "COMILLA"]


def test_cadena_sin_cerrar():
    with pytest.raises(ValueError, match="Cadena sin cerrar"):
        tokenizar("ubicacion('Tunja")


@pytest.mark.parametrize("numero", ["4.7.1", "4.", "-4.7.1"])
def test_numero_mal_formado(numero):
    with pytest.raises(ValueError, match="Número mal formado"):
        tokenizar(f"coordenada({numero}, 1)")


def test_decimal_sin_parte_entera_sugiere_cero():
    with pytest.raises(ValueError, match="escribe 0.5"):
        tokenizar("coordenada(.5, 1)")


@pytest.mark.parametrize("caracter", ["$", "+", "[", ";"])
def test_caracter_no_reconocido(caracter):
    with pytest.raises(ValueError, match="Carácter no reconocido"):
        tokenizar(f"coordenada(1{caracter} 2)")


def test_guion_suelto_no_es_negativo():
    with pytest.raises(ValueError, match="Carácter no reconocido: '-'"):
        tokenizar("coordenada(4, - 74)")
