import os
import sys

import pytest

# Los módulos del compilador están en src/ y se importan entre sí por nombre (como en Docker)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import ServicioGeografico  # noqa: E402


# Respuestas simuladas de Nominatim, para que las pruebas no usen internet
LUGARES = {
    "tunja": [{"display_name": "Tunja, Boyacá, Colombia", "lat": "5.5324", "lon": "-73.3616"}],
    "san andrés": [{"display_name": "Isla de San Andrés, Colombia", "lat": "12.5376", "lon": "-81.7204"}],
    "bogota": [{"display_name": "Bogotá, Distrito Capital, Colombia", "lat": "4.6534", "lon": "-74.0836"}],
}


@pytest.fixture(autouse=True)
def servicio_simulado(monkeypatch):
    """Reemplaza la consulta HTTP a Nominatim por datos fijos y limpia la caché."""
    consultas = []

    def consultar(ruta, parametros):
        consultas.append((ruta, parametros))
        if ruta == "search":
            return LUGARES.get(parametros["q"].strip().lower(), [])
        if ruta == "reverse":
            if parametros["lat"] == 0 and parametros["lon"] == -30:     # océano Atlántico
                return {"error": "Unable to geocode"}
            return {"display_name": "Tunja, Boyacá, Colombia"}
        raise AssertionError(f"ruta inesperada: {ruta}")

    monkeypatch.setattr(ServicioGeografico, "_consultar", consultar)
    ServicioGeografico._cache.clear()
    yield consultas
    ServicioGeografico._cache.clear()
