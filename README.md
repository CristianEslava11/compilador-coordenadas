# Librería de Coordenadas Geográficas

Proyecto académico desarrollado para la asignatura de **Lenguajes Formales y Compiladores** de la UPTC.

El objetivo del proyecto es construir un lenguaje de dominio específico (DSL) para trabajar con coordenadas geográficas y ofrecerlo a través de tres modos de ejecución: línea de comandos, interfaz web y aplicación de escritorio.

---

## 1. Objetivo del proyecto

El compilador permite:

- validar coordenadas geográficas
- consultar lugares a partir de una coordenada
- calcular distancias entre puntos
- identificar hemisferios
- buscar ubicaciones por nombre

La lógica principal se implementa en Python, mientras que la interfaz se presenta en HTML/CSS/JavaScript y, para la versión escritorio, se usa una ventana nativa con pywebview.

---

## 2. Estructura del proyecto

```text
Compilador-Coordenadas/
├── Dockerfile
├── docker-compose.yml
├── README.md
├── DOCUMENTACION.md
├── docs/
│   └── Pseudocodigo.txt
├── imagenes/
├── ProgramasCompilador/
│   ├── ejemplo.geo
│   └── ...
├── src/
│   ├── AnalisiLexicoCoordenadas.py   # Analizador léxico
│   ├── AnalisisSintactico.py         # Parser y búsqueda de reglas
│   ├── ReglasSintacticas.py          # Validación sintáctica y ejecución
│   ├── Token.py                     # Clase Token
│   ├── main.py                      # CLI del compilador
│   ├── servidor.py                  # API FastAPI para la versión web
│   ├── app.py                       # Orquestador de la versión escritorio
│   ├── requirements.txt             # Dependencias del proyecto
│   ├── geo.spec                    # Configuración de PyInstaller
│   ├── persistencia/
│   │   └── reglas.json              # Reglas del lenguaje
│   └── ui/
│       ├── index.html               # Interfaz principal web/escritorio
│       ├── main.js                  # Lógica del frontend
│       ├── mapa.js                 # Render del mapa y coordenadas
│       ├── style.css               # Estilos visuales
│       └── vendor/
│           ├── d3.min.js
│           ├── mundo-50m.js
│           └── topojson-client.min.js
└── src/build/                       # Archivos generados por PyInstaller
```

---

## 3. Arquitectura del proyecto

El proyecto está compuesto por tres capas:

1. **Lógica del compilador**
   - Se encarga del análisis léxico y sintáctico.
   - Está en los archivos de la carpeta `src`.

2. **API web**
   - El backend se expone con FastAPI usando `servidor.py`.
   - Recibe instrucciones en lenguaje GEO y devuelve resultados o errores.

3. **Interfaz gráfica**
   - La parte visual está en `src/ui`.
   - La versión web se sirve desde FastAPI.
   - La versión escritorio abre una ventana nativa con pywebview y levanta el backend en segundo plano.

---

## 4. Lenguaje de comandos

### 4.1 Validación de coordenadas

```text
validacion(latitud, longitud)
```

Ejemplos:

```text
validacion(4.7110, -74.0721)
validacion(95.0, -74.0721)
```

Reglas:
- la latitud debe estar entre `-90` y `90`
- la longitud debe estar entre `-180` y `180`

### 4.2 Consulta de coordenada

```text
coordenada(latitud, longitud)
```

Ejemplo:

```text
coordenada(4.7110, -74.0721)
```

### 4.3 Distancia entre coordenadas

```text
distancia(latitud1, longitud1), (latitud2, longitud2)
```

Ejemplo:

```text
distancia(4.7110, -74.0721), (6.2442, -75.5812)
```

### 4.4 Hemisferio

```text
hemisferio(latitud, longitud)
```

Ejemplo:

```text
hemisferio(4.7110, -74.0721)
```

### 4.5 Búsqueda por ubicación

```text
ubicacion('Colombia')
```

Ejemplo:

```text
ubicacion('Bogotá')
```

---

## 5. Reglas sintácticas del lenguaje

* Toda instrucción debe iniciar con una palabra reservada válida: `coordenada`, `validacion`, `distancia`, `hemisferio` o `ubicacion`.
* Una coordenada se representa como `(latitud, longitud)`.
* La separación de argumentos se realiza con `,`.
* Los textos de ubicación se escriben entre comillas simples o dobles según el caso de uso.

Ejemplos válidos:

```text
coordenada(4.7110, -74.0721)
validacion(4.7110, -74.0721)
distancia(4.7110, -74.0721), (6.2442, -75.5812)
hemisferio(4.7110, -74.0721)
ubicacion('Colombia')
```

---

## 6. Ejecución del compilador

### 6.1 Requisitos

- Python 3.x
- Dependencias del proyecto:

```bash
pip install -r src/requirements.txt
```

### 6.2 Modo línea de comandos

```bash
python src/main.py
```

Ejemplo:

```text
GEO> coordenada(4.7110, -74.0721)
```

### 6.3 Ejecutar solo el analizador léxico

```bash
python src/AnalisiLexicoCoordenadas.py
```

---

## 7. Ejecución web

La versión web usa FastAPI como backend.

1. Instala las dependencias:

```bash
pip install -r src/requirements.txt
```

2. Ejecuta el servidor:

```bash
uvicorn servidor:app --host 0.0.0.0 --port 8000
```

3. Abre en el navegador:

```text
http://localhost:8000
```

La interfaz principal queda en:

```text
http://localhost:8000/ui/index.html
```

---

## 8. Ejecución de escritorio

La aplicación de escritorio se ejecuta desde `src/app.py`.

```bash
python src/app.py
```

Esta versión:
- levanta el backend FastAPI en segundo plano
- abre una ventana nativa con pywebview
- carga la interfaz web dentro de la ventana del sistema

---

## 9. Ejecución con Docker

El proyecto incluye un `Dockerfile` y un `docker-compose.yml` para ejecutar la aplicación en contenedor.

### Opción 1: con Docker Compose

```bash
docker compose up --build
```

Luego abre:

```text
http://localhost:8000
```

### Opción 2: construcción manual

```bash
docker build -t compilador-coordenadas .
docker run -d -p 8000:8000 --name compilador-coordenadas compilador-coordenadas
```

Para detenerlo:

```bash
docker stop compilador-coordenadas
```

---

## 10. Generación del ejecutable Windows

Para empaquetar la versión escritorio con PyInstaller, ejecuta:

```bash
cd src
pyinstaller geo.spec
```

El ejecutable generado quedará en:

```text
src/dist/GeoQuery.exe
```

---

## 11. Tecnologías utilizadas

- Python 3
- FastAPI
- Uvicorn
- HTML + CSS + JavaScript
- pywebview
- PyInstaller
- Docker y Docker Compose

---

## 12. Tokens reconocidos

| Token | Descripción | Ejemplo |
|-------|-------------|---------|
| `IDENTIFICADOR` | Palabra clave reservada | `coordenada` |
| `STRING` | Texto literal | `Colombia` |
| `NUMERO` | Número entero o decimal | `45.12` |
| `NEGATIVO` | Número negativo | `-19.43` |
| `LPARENT` | Paréntesis de apertura | `(` |
| `RPARENT` | Paréntesis de cierre | `)` |
| `COMA` | Separador de argumentos | `,` |
| `COMILLA` | Comillas simples | `'` |

Palabras clave principales:

```text
coordenada | ubicacion | distancia | hemisferio | validar
```

---

## 13. Estado del proyecto

- [x] Diseño de autómatas del lenguaje.
- [x] Analizador léxico inicial.
- [x] Parser con reglas dinámicas.
- [x] Interfaz web.
- [x] Interfaz de escritorio.
- [x] Ejecución con Docker.
- [x] Empaquetado con PyInstaller.
- [ ] Validación semántica completa de rangos geográficos.
- [ ] Cálculo total de distancias y localización por hemisferios.
- [ ] Consulta completa de lugares y coordenadas.

---

## 14. Autora

Proyecto desarrollado como parte de la formación en Ingeniería de Sistemas – UPTC.

---

## 15. Referencias visuales

Los autómatas y diagramas del compilador se encuentran en la carpeta `imagenes/` y en la documentación del proyecto.
