import Compilador
import ServicioGeografico
from Compilador import MAX_CONSULTAS_SERVICIO, compilar_instruccion, compilar_programa


def test_instruccion_correcta_pasa_todas_las_fases():
    i = compilar_instruccion("distancia(4.7110, -74.0721), (6.2442, -75.5812)", 3)
    assert i["exito"] is True
    assert i["linea"] == 3
    assert i["resultado"]["comando"] == "distancia"
    assert i["salida"] == {"kilometros": 238.67}
    assert all(t["linea"] == 3 for t in i["tokens"])


def test_fase_de_cada_error():
    casos = {
        "coordenada(4, $)": "lexico",
        "coordenada(4 5)": "sintactico",
        "coordenada(1, 2) validar(3, 4)": "sintactico",
        "coordenada(95, 5)": "semantico",
        "ubicacion('Atlantida')": "ejecucion",
    }
    for texto, fase in casos.items():
        i = compilar_instruccion(texto, 1)
        assert (i["exito"], i["fase"]) == (False, fase), texto


def test_error_semantico_conserva_el_arbol_y_los_tokens():
    i = compilar_instruccion("coordenada(95, 5)", 1)
    assert i["resultado"] == {"comando": "coordenada", "argumentos": (95.0, 5.0)}
    assert len(i["tokens"]) == 6


def test_servicio_caido_es_error_de_ejecucion(monkeypatch):
    def sin_conexion(ruta, parametros):
        raise ServicioGeografico.ErrorServicioGeografico("No se pudo consultar el servicio")
    monkeypatch.setattr(ServicioGeografico, "_consultar", sin_conexion)

    i = compilar_instruccion("ubicacion('Tunja')", 1)
    assert (i["exito"], i["fase"]) == (False, "ejecucion")


def test_programa_ignora_vacias_y_comentarios_y_numera_lineas():
    programa = "# comentario\n\ncoordenada(5.5353, -73.3678)\n   \nhemisferio(-33.8, 151.2)\n"
    instrucciones = compilar_programa(programa)
    assert [i["linea"] for i in instrucciones] == [3, 5]
    assert all(i["exito"] for i in instrucciones)


def test_un_error_no_detiene_las_demas_lineas():
    instrucciones = compilar_programa("coordenada(4 5)\nvalidar(1, 2)\ncoordenada(95, 1)")
    assert [i["exito"] for i in instrucciones] == [False, True, False]


def test_limite_de_consultas_al_servicio():
    programa = "\n".join(["ubicacion('Tunja')"] * (MAX_CONSULTAS_SERVICIO + 2) + ["hemisferio(1, 2)"])
    instrucciones = compilar_programa(programa)
    ubicaciones = instrucciones[:-1]
    assert sum(i["exito"] for i in ubicaciones) == MAX_CONSULTAS_SERVICIO
    assert "límite" in ubicaciones[-1]["error"]
    # Las instrucciones que no consultan el servicio no se ven afectadas
    assert instrucciones[-1]["exito"] is True


def test_error_inesperado_es_interno(monkeypatch):
    def falla(resultado):
        raise KeyError("x")
    monkeypatch.setattr(Compilador, "ejecutar", falla)
    i = compilar_instruccion("validar(1, 2)", 1)
    assert (i["exito"], i["fase"]) == (False, "interno")
