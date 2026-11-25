# Cliente de Nominatim (OpenStreetMap) para buscar lugares por nombre y
# obtener el lugar que corresponde a una coordenada.
#
# Política de uso de Nominatim (https://operations.osmfoundation.org/policies/nominatim/):
#   - máximo 1 consulta por segundo
#   - identificar la aplicación con un User-Agent propio
#   - guardar en caché los resultados en vez de repetir consultas
#   - dar crédito: "© OpenStreetMap contributors"

import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

URL_BASE = "https://nominatim.openstreetmap.org"
USER_AGENT = "GeoQuery/1.0 (proyecto academico UPTC; +https://github.com/CristianEslava11/compilador-coordenadas)"
ATRIBUCION = "© OpenStreetMap contributors"
TIEMPO_ESPERA = 10          # segundos máximos por consulta
INTERVALO_MINIMO = 1.0      # segundos entre consultas

_cache = {}
_candado = threading.Lock()
_ultima_consulta = 0.0


class ErrorServicioGeografico(Exception):
    pass


def _consultar(ruta, parametros):
    """Hace una petición GET a Nominatim respetando 1 consulta/segundo."""
    global _ultima_consulta
    parametros = {**parametros, "format": "jsonv2", "accept-language": "es"}
    url = f"{URL_BASE}/{ruta}?{urllib.parse.urlencode(parametros)}"
    peticion = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    # El candado hace que las consultas vayan de una en una, aunque lleguen
    # varias peticiones al servidor al mismo tiempo
    with _candado:
        espera = INTERVALO_MINIMO - (time.monotonic() - _ultima_consulta)
        if espera > 0:
            time.sleep(espera)
        try:
            with urllib.request.urlopen(peticion, timeout=TIEMPO_ESPERA) as respuesta:
                return json.loads(respuesta.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            if error.code in (403, 429):
                raise ErrorServicioGeografico(
                    "El servicio de ubicaciones (OpenStreetMap) rechazó la consulta por exceso de "
                    "peticiones. Intenta de nuevo en unos minutos.")
            raise ErrorServicioGeografico(f"El servicio de ubicaciones respondió con un error (HTTP {error.code})")
        except (urllib.error.URLError, TimeoutError, OSError):
            raise ErrorServicioGeografico(
                "No se pudo consultar el servicio de ubicaciones (OpenStreetMap). "
                "Verifica la conexión a internet.")
        finally:
            _ultima_consulta = time.monotonic()


def buscar_lugar(nombre):
    """Busca un lugar por nombre. Devuelve {"nombre", "latitud", "longitud"} o None si no existe."""
    clave = ("buscar", nombre.strip().lower())
    if clave not in _cache:
        resultados = _consultar("search", {"q": nombre, "limit": 1})
        if resultados:
            lugar = resultados[0]
            _cache[clave] = {
                "nombre": lugar.get("display_name", nombre),
                "latitud": float(lugar["lat"]),
                "longitud": float(lugar["lon"]),
            }
        else:
            _cache[clave] = None
    return _cache[clave]


def lugar_de_coordenada(latitud, longitud):
    """Devuelve el nombre del lugar en esa coordenada (ciudad o región), o None
    si no hay ninguno (por ejemplo, en medio del océano)."""
    clave = ("inversa", round(latitud, 4), round(longitud, 4))
    if clave not in _cache:
        # zoom=10 pide el resultado a nivel de ciudad
        respuesta = _consultar("reverse", {"lat": latitud, "lon": longitud, "zoom": 10})
        _cache[clave] = respuesta.get("display_name") if "error" not in respuesta else None
    return _cache[clave]
