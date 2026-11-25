import pytest

from Ejecucion import ErrorEjecucion, ejecutar, haversine


def test_distancia_bogota_medellin():
    salida = ejecutar({"comando": "distancia", "argumentos": ((4.7110, -74.0721), (6.2442, -75.5812))})
    assert salida == {"kilometros": 238.67}


def test_haversine_casos_conocidos():
    assert haversine(4.7, -74.0, 4.7, -74.0) == 0
    # Medio ecuador: π · R
    assert haversine(0, 0, 0, 180) == pytest.approx(20015.11, abs=0.01)
    # Polo a polo
    assert haversine(90, 0, -90, 0) == pytest.approx(20015.11, abs=0.01)


@pytest.mark.parametrize("latitud, longitud, esperado", [
    (4.7, -74.0, ("Norte", "Oeste")),
    (-33.8, 151.2, ("Sur", "Este")),
    (0, 10, ("Ecuador (límite entre Norte y Sur)", "Este")),
    (10, 0, ("Norte", "Meridiano de Greenwich (límite entre Este y Oeste)")),
    (-10, 180, ("Sur", "Antimeridiano (límite entre Este y Oeste)")),
    (-10, -180, ("Sur", "Antimeridiano (límite entre Este y Oeste)")),
])
def test_hemisferio(latitud, longitud, esperado):
    salida = ejecutar({"comando": "hemisferio", "argumentos": (latitud, longitud)})
    assert (salida["latitudinal"], salida["longitudinal"]) == esperado


def test_validar():
    assert ejecutar({"comando": "validar", "argumentos": (4.7, -74.0)}) == {"valida": True, "motivos": []}
    salida = ejecutar({"comando": "validar", "argumentos": (95, 10)})
    assert salida["valida"] is False
    assert len(salida["motivos"]) == 1


def test_ubicacion_encontrada():
    salida = ejecutar({"comando": "ubicacion", "argumentos": "Tunja"})
    assert salida["nombre"] == "Tunja, Boyacá, Colombia"
    assert (salida["latitud"], salida["longitud"]) == (5.5324, -73.3616)
    assert "OpenStreetMap" in salida["fuente"]


def test_ubicacion_no_encontrada():
    with pytest.raises(ErrorEjecucion, match="No se encontró ningún lugar llamado 'Atlantida'"):
        ejecutar({"comando": "ubicacion", "argumentos": "Atlantida"})


def test_coordenada_devuelve_el_lugar():
    salida = ejecutar({"comando": "coordenada", "argumentos": (5.5353, -73.3678)})
    assert salida["lugar"] == "Tunja, Boyacá, Colombia"


def test_coordenada_en_el_oceano_no_tiene_lugar():
    salida = ejecutar({"comando": "coordenada", "argumentos": (0, -30)})
    assert salida["lugar"] is None


def test_consultas_repetidas_usan_la_cache(servicio_simulado):
    ejecutar({"comando": "ubicacion", "argumentos": "Tunja"})
    ejecutar({"comando": "ubicacion", "argumentos": "  TUNJA "})
    assert len(servicio_simulado) == 1
