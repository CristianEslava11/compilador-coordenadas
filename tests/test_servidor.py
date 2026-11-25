import warnings

import pytest

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from fastapi.testclient import TestClient

from servidor import app


@pytest.fixture
def cliente():
    return TestClient(app)


def test_raiz_redirige_al_navegador_a_la_interfaz(cliente):
    respuesta = cliente.get("/", headers={"accept": "text/html"}, follow_redirects=False)
    assert respuesta.status_code == 307
    assert respuesta.headers["location"] == "/ui/"


def test_raiz_devuelve_json_a_clientes_de_la_api(cliente):
    assert cliente.get("/").json() == cliente.get("/info").json()


def test_info(cliente):
    datos = cliente.get("/info").json()
    assert datos["lenguaje"] == "GEO"
    assert "OpenStreetMap" in datos["datos_geograficos"]


def test_interfaz_se_sirve_y_se_revalida(cliente):
    respuesta = cliente.get("/ui/")
    assert respuesta.status_code == 200
    assert "GeoQuery" in respuesta.text
    assert respuesta.headers["cache-control"] == "no-cache"


def test_iniciar_programa(cliente):
    codigo = "# prueba\nvalidar(4.7, -74.0)\ncoordenada(95, 1)"
    datos = cliente.post("/iniciar", json={"codigo": codigo}).json()
    assert datos["exito"] is False
    assert datos["error"].startswith("Línea 3:")
    assert [i["linea"] for i in datos["instrucciones"]] == [2, 3]
    assert datos["instrucciones"][0]["salida"] == {"valida": True, "motivos": []}
    assert datos["instrucciones"][1]["fase"] == "semantico"
    assert len(datos["tokens"]) == 12


def test_iniciar_sin_codigo(cliente):
    datos = cliente.post("/iniciar", json={"codigo": "  \n# solo comentario"}).json()
    assert datos == {"exito": False, "error": "No se ingresó código", "instrucciones": [], "tokens": []}
