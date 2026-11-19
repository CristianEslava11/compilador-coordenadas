"""Pruebas de humo: aseguran que lo que ya funciona sigue funcionando
mientras se cambia la arquitectura. Ejecutar con:  pytest -q"""
from fastapi.testclient import TestClient

from servidor import app

cliente = TestClient(app)


def test_estado_json():
    r = cliente.get("/")
    assert r.status_code == 200
    assert r.json()["lenguaje"] == "GEO"


def test_navegador_redirige_a_ui():
    r = cliente.get("/", headers={"accept": "text/html"}, follow_redirects=False)
    assert r.status_code in (302, 307)
    assert r.headers["location"] == "/ui/"


def test_ui_se_sirve():
    r = cliente.get("/ui/")
    assert r.status_code == 200
    assert "GeoQuery" in r.text
    for recurso in ("main.js", "mapa.js", "style.css", "vendor/d3.min.js"):
        assert cliente.get(f"/ui/{recurso}").status_code == 200


def test_instrucciones_validas():
    codigo = "\n".join([
        "coordenada(4.7110, -74.0721)",
        "# comentario ignorado",
        "hemisferio(4.7110, -74.0721)",
        "distancia(4.7110, -74.0721), (6.2442, -75.5812)",
        "ubicacion('Bogota')",
    ])
    data = cliente.post("/iniciar", json={"codigo": codigo}).json()
    assert data["exito"] is True
    assert [i["linea"] for i in data["instrucciones"]] == [1, 3, 4, 5]
    assert data["instrucciones"][0]["resultado"]["comando"] == "coordenada"


def test_error_sintactico_reporta_linea():
    data = cliente.post("/iniciar", json={"codigo": "coordenada(4.7)\ncoordenada 4.7"}).json()
    assert data["exito"] is False
    assert data["error"].startswith("Línea")


def test_codigo_vacio():
    data = cliente.post("/iniciar", json={"codigo": "   "}).json()
    assert data["exito"] is False
