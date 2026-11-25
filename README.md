# GeoQuery — Compilador de Coordenadas Geográficas

Proyecto académico de la asignatura **Lenguajes Formales y Compiladores** de la UPTC.

GeoQuery es un compilador para **GEO**, un lenguaje de dominio específico (DSL) para trabajar con coordenadas geográficas: validar coordenadas, calcular distancias, identificar hemisferios, buscar lugares por nombre y obtener el lugar que corresponde a una coordenada.

El compilador implementa las cuatro fases **léxica → sintáctica → semántica → ejecución** y se puede usar de tres formas: una **interfaz gráfica** con editor y mapa (aplicación de escritorio o web), una **consola** (CLI) y una **API REST**.

---

## El lenguaje GEO

Un programa GEO tiene **una instrucción por línea**. Las líneas vacías se ignoran y las que empiezan con `#` son comentarios. Las palabras clave no distinguen mayúsculas de minúsculas.

```text
# Programa de ejemplo
COORDENADA(5.5353, -73.3678)
VALIDAR(95, -200)
DISTANCIA(4.7110, -74.0721), (6.2442, -75.5812)
HEMISFERIO(-33.8688, 151.2093)
UBICACION('San Andrés')
```

### Instrucciones

| Instrucción | Sintaxis | Resultado | Ejemplo de salida |
|---|---|---|---|
| `COORDENADA` | `coordenada(lat, lon)` | Lugar que corresponde a la coordenada | `Tunja, Boyacá, Colombia` |
| `VALIDAR` | `validar(lat, lon)` | Si la coordenada es válida y, si no, por qué | `Coordenada inválida: latitud 95 fuera de rango…` |
| `DISTANCIA` | `distancia(lat1, lon1), (lat2, lon2)` | Distancia en km sobre la superficie terrestre (fórmula de Haversine) | `238.67 km` |
| `HEMISFERIO` | `hemisferio(lat, lon)` | Hemisferio Norte/Sur y Este/Oeste | `Sur · Este` |
| `UBICACION` | `ubicacion('lugar')` | Coordenadas del lugar buscado | `Isla de San Andrés, Colombia (12.5376, -81.7204)` |

- La **latitud** debe estar entre `-90` y `90`, y la **longitud** entre `-180` y `180`.
- En `HEMISFERIO`, los puntos sobre el ecuador, el meridiano de Greenwich o el antimeridiano (±180°) se reportan como límite entre hemisferios.
- El nombre del lugar en `UBICACION` va entre comillas simples y puede tener espacios, tildes y puntos: `ubicacion('Bogotá D.C.')`.
- `COORDENADA` y `UBICACION` consultan el servicio Nominatim de OpenStreetMap, así que **requieren conexión a internet**.

### Gramática

Gramática en notación EBNF. Los símbolos en MAYÚSCULAS son tokens del analizador léxico.

```ebnf
programa     = { linea } ;
linea        = ( instruccion | comentario | vacia ) FIN_DE_LINEA ;
comentario   = "#" { cualquier_caracter } ;
vacia        = { espacio } ;

instruccion  = coordenada_i | validar_i | distancia_i | hemisferio_i | ubicacion_i ;

coordenada_i = "coordenada" coordenada ;
validar_i    = "validar"    coordenada ;
hemisferio_i = "hemisferio" coordenada ;
distancia_i  = "distancia"  coordenada COMA coordenada ;
ubicacion_i  = "ubicacion"  LPARENT COMILLA STRING COMILLA RPARENT ;

coordenada   = LPARENT numero COMA numero RPARENT ;
numero       = NUMERO | NEGATIVO ;
```

> Los comentarios ocupan una línea completa: no se puede escribir un comentario después de una instrucción en la misma línea.

### Tokens

| Token | Descripción | Expresión regular | Ejemplo |
|---|---|---|---|
| `IDENTIFICADOR` | Palabra clave del lenguaje | `coordenada \| validar \| distancia \| hemisferio \| ubicacion` | `distancia` |
| `NUMERO` | Número positivo, entero o decimal | `[0-9]+(\.[0-9]+)?` | `4.7110` |
| `NEGATIVO` | Número negativo, entero o decimal | `-[0-9]+(\.[0-9]+)?` | `-74.0721` |
| `STRING` | Texto entre comillas, o palabra que no es clave | `'[^']*'` / `[a-zA-Z]+` | `San Andrés` |
| `LPARENT` | Paréntesis de apertura | `\(` | `(` |
| `RPARENT` | Paréntesis de cierre | `\)` | `)` |
| `COMA` | Separador | `,` | `,` |
| `COMILLA` | Delimitador de cadenas | `'` | `'` |

---

## Arquitectura del compilador

```text
código fuente ─► Léxico ─► tokens ─► Sintáctico ─► árbol ─► Semántico ─► Ejecución ─► resultado
                  │                    │                     │              │
        AnalisiLexico...py   AnalisisSintactico.py   AnalisisSemantico.py  Ejecucion.py
                             ReglasSintacticas.py                          ServicioGeografico.py
                             persistencia/reglas.json
```

`Compilador.py` orquesta las fases para cada línea del programa. Lo usan por igual la consola (`main.py`), la API (`servidor.py`) y la interfaz gráfica, de modo que un programa `.geo` se comporta igual en todas.

| Fase | Módulo | Qué hace | Ejemplo de error |
|---|---|---|---|
| Léxica | `AnalisiLexicoCoordenadas.py` | Recorre el texto carácter a carácter (autómata finito) y genera los tokens | `Número mal formado: '4.7.1'` |
| Sintáctica | `AnalisisSintactico.py`, `ReglasSintacticas.py`, `persistencia/reglas.json` | Verifica la estructura y construye el árbol `{comando, argumentos}` | `Se esperaba ',' entre latitud y longitud` |
| Semántica | `AnalisisSemantico.py` | Verifica que los valores tengan sentido geográfico (rangos de latitud y longitud) | `Latitud 95 fuera de rango (debe estar entre -90 y 90)` |
| Ejecución | `Ejecucion.py`, `ServicioGeografico.py` | Calcula el resultado de la instrucción | `No se encontró ningún lugar llamado 'xyz'` |

**Recuperación de errores:** cada línea se compila de forma independiente. Un error en una línea no detiene las demás, así se reportan todos los errores del programa en una sola ejecución, cada uno con su línea y su fase.

### Análisis sintáctico dirigido por configuración

El parser no tiene las reglas escritas en su código. Lee `persistencia/reglas.json`, que asocia cada palabra clave con las funciones que validan su estructura:

```json
"distancia": {
    "funcion_clave": "revisar_palabra_clave",
    "funcion_argumentos": "regla_distancia"
}
```

Con el primer token de la línea, el parser busca la regla en el JSON e invoca dinámicamente (`getattr`) las funciones de `ReglasSintacticas.py`, que consumen los tokens esperados y avanzan la posición del parser. El resultado es el árbol:

```python
{"comando": "distancia", "argumentos": ((4.711, -74.0721), (6.2442, -75.5812))}
```

El análisis semántico y la ejecución siguen el mismo patrón: un diccionario asocia cada comando con su regla o su acción.

### Servicio geográfico (Nominatim / OpenStreetMap)

`ServicioGeografico.py` consulta [Nominatim](https://nominatim.org/) para `UBICACION` (búsqueda por nombre) y `COORDENADA` (búsqueda inversa), respetando su [política de uso](https://operations.osmfoundation.org/policies/nominatim/):

- máximo **1 consulta por segundo**, aunque lleguen varias peticiones a la vez;
- `User-Agent` propio que identifica la aplicación;
- **caché** de resultados, para no repetir consultas;
- máximo **15 consultas por programa**;
- si no hay internet o el servicio rechaza la consulta, la instrucción termina con un error de ejecución y el resto del programa sigue.

### Autómatas

Diagramas de las reglas léxicas y sintácticas de cada instrucción:

| Instrucción | Autómata |
|---|---|
| Validación | ![Autómata de validación](imagenes/Diagrama%20automata%20%20validaci%C3%B3n.png) |
| Coordenada | ![Autómata de coordenada](imagenes/Diagrama%20automata%20coordenada.png) |
| Distancia | ![Autómata de distancia](imagenes/Diagrama%20automata%20distancia.png) |
| Hemisferio | ![Autómata de hemisferio](imagenes/Diagrama%20automata%20hemisferio.png) |
| Ubicación | ![Autómata de ubicación](imagenes/Diagrama%20automata%20%20ubicacion.png) |

Flujo del analizador sintáctico:

![Diagrama del Analizador Sintáctico](imagenes/diagrama%20analizador%20sintactico.png)

---

## Interfaz gráfica

La interfaz (`src/ui/`) está hecha con HTML, CSS y JavaScript, y la sirve el mismo backend en `/ui/`. Incluye:

- **Editor** con resaltado de sintaxis, números de línea y las líneas con error marcadas en rojo.
- **Panel de instrucciones** para insertar ejemplos de cada comando.
- **Mapa mundial vectorial** (d3 + datos de Natural Earth, funciona sin internet) que dibuja los puntos, las rutas de `DISTANCIA` con su distancia en km y los lugares encontrados con `UBICACION`. Al hacer clic en una instrucción del resultado, el mapa se enfoca en ella.
- **Pestañas** de Resultado, Tokens y Árbol sintáctico, y un indicador del estado de cada fase del compilador.

### API REST (`servidor.py`)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Desde un navegador, redirige a la interfaz (`/ui/`); desde otros clientes, devuelve lo mismo que `/info` |
| `GET` | `/info` | Información del lenguaje y la versión |
| `POST` | `/iniciar` | Compila un programa: `{"codigo": "..."}` |
| `GET` | `/docs` | Documentación interactiva de la API (Swagger) |

Respuesta de `/iniciar` (resumida):

```json
{
  "exito": false,
  "error": "Línea 2: Latitud 95 fuera de rango (debe estar entre -90 y 90)",
  "instrucciones": [
    {"linea": 1, "codigo": "distancia(4.7110, -74.0721), (6.2442, -75.5812)", "exito": true,
     "resultado": {"comando": "distancia", "argumentos": [[4.711, -74.0721], [6.2442, -75.5812]]},
     "salida": {"kilometros": 238.67}, "tokens": ["..."]},
    {"linea": 2, "codigo": "coordenada(95, 10)", "exito": false,
     "fase": "semantico", "error": "Latitud 95 fuera de rango (debe estar entre -90 y 90)", "tokens": ["..."]}
  ],
  "tokens": ["..."]
}
```

---

## Ejecución

Requisitos: **Python 3.12 o superior**. Los comandos de esta sección se ejecutan desde la carpeta `src/`, salvo que se indique otra cosa.

```bash
pip install -r requirements.txt
```

| Modo | Comando | Dónde |
|---|---|---|
| Aplicación de escritorio | `python app.py` | Ventana nativa |
| Web (navegador) | `python -m uvicorn servidor:app --reload` | `http://127.0.0.1:8000/` |
| Consola interactiva | `python main.py` | `GEO>` (escribe `CERRAR` para salir) |
| Ejecutar un archivo | `python main.py ../ProgramasCompilador/ejemplo.geo` | Consola |
| Ayuda de la consola | `python main.py --help` | Consola |
| Docker (desde la raíz) | `docker compose up --build` | `http://localhost:8000/` |

### Generar el ejecutable (.exe)

Con todas las ventanas de GeoQuery cerradas, desde `src/`:

```bash
pip install pyinstaller
pyinstaller geo.spec
```

El ejecutable queda en **`src/dist/GeoQuery.exe`**. La aplicación levanta el servidor en un puerto libre y abre la interfaz en una ventana propia, así que se pueden abrir varias a la vez.

### Despliegue en Render

El repositorio incluye `Dockerfile` y `render.yaml`. En [render.com](https://render.com): **New → Blueprint**, seleccionar este repositorio y aplicar. Render crea el servicio con el plan *Free*, lo despliega desde la rama `main` y lo vuelve a desplegar en cada push a `main`. El servicio queda en `https://<nombre>.onrender.com/`.

En el plan gratuito el servicio se suspende tras unos 15 minutos sin uso; la primera visita después de eso tarda entre 30 y 60 segundos.

### Pruebas

Desde la raíz del proyecto:

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Las pruebas cubren las cuatro fases, el compilador y la API. Simulan el servicio de Nominatim, así que no necesitan internet.

**Integración continua:** en cada pull request y en cada push a `main`, GitHub Actions (`.github/workflows/ci.yml`) ejecuta las pruebas, construye la imagen de Docker y comprueba que el contenedor sirve la interfaz.

---

## Tecnologías

- **Python 3** — compilador (léxico, sintáctico, semántico y ejecución), construido desde cero sin generadores de parsers.
- **FastAPI** y **Uvicorn** — API REST y servidor de la interfaz.
- **HTML, CSS y JavaScript** — interfaz gráfica; **d3** y **topojson-client** para el mapa.
- **pywebview** — ventana nativa de la aplicación de escritorio.
- **PyInstaller** — empaquetado como ejecutable de Windows.
- **Docker**, **Docker Compose** y **Render** — contenedor y despliegue en línea.
- **pytest** y **GitHub Actions** — pruebas automáticas e integración continua.
- **Nominatim (OpenStreetMap)** — búsqueda de lugares.

En [`DOCUMENTACION.md`](DOCUMENTACION.md) hay un resumen del contexto, las motivaciones y la arquitectura del proyecto.

---

## Estructura del proyecto

```text
Compilador-Coordenadas/
├── src/
│   ├── Token.py                     # Clase Token (tipo, valor)
│   ├── AnalisiLexicoCoordenadas.py  # Fase léxica
│   ├── AnalisisSintactico.py        # Motor del parser (carga reglas.json)
│   ├── ReglasSintacticas.py         # Reglas sintácticas de cada instrucción
│   ├── AnalisisSemantico.py         # Fase semántica (rangos)
│   ├── Ejecucion.py                 # Fase de ejecución (intérprete)
│   ├── ServicioGeografico.py        # Cliente de Nominatim (OpenStreetMap)
│   ├── Compilador.py                # Orquesta las fases para cada línea
│   ├── main.py                      # Consola (CLI)
│   ├── servidor.py                  # API REST + interfaz web (FastAPI)
│   ├── app.py                       # Aplicación de escritorio (pywebview)
│   ├── geo.spec                     # Configuración de PyInstaller
│   ├── requirements.txt             # Dependencias (escritorio y CLI)
│   ├── requirements-web.txt         # Dependencias del servidor (Docker)
│   ├── persistencia/reglas.json     # Reglas sintácticas en JSON
│   └── ui/                          # Interfaz: index.html, style.css, main.js, mapa.js, vendor/
├── tests/                           # Pruebas automáticas (pytest)
├── ProgramasCompilador/ejemplo.geo  # Programa de ejemplo
├── imagenes/                        # Diagramas de los autómatas
├── docs/                            # Pseudocódigo del analizador léxico
├── .github/workflows/ci.yml         # Integración continua (pruebas + Docker)
├── Dockerfile, docker-compose.yml   # Contenedor del servidor
├── render.yaml                      # Despliegue en Render
└── DOCUMENTACION.md                 # Contexto y arquitectura del proyecto
```

---

## Créditos

- Datos de lugares: © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), mediante el servicio [Nominatim](https://nominatim.org/).
- Mapa base: [Natural Earth](https://www.naturalearthdata.com/) (dominio público), a través de [world-atlas](https://github.com/topojson/world-atlas).
- Visualización del mapa: [d3](https://d3js.org/) y [topojson-client](https://github.com/topojson/topojson-client).

## Autores

Cristian Eslava y Kimberly Figueroa — Ingeniería de Sistemas, Universidad Pedagógica y Tecnológica de Colombia (UPTC).
