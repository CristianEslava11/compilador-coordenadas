# Librería de Coordenadas Geográficas

Proyecto académico desarrollado para la asignatura de **Lenguajes Formales y Compiladores** de la UPTC.

El objetivo es construir una librería y un lenguaje de dominio específico (DSL) para trabajar con coordenadas geográficas. Las instrucciones permitirán validar coordenadas, consultar lugares, calcular distancias, identificar hemisferios y obtener coordenadas a partir de una ubicación.

Actualmente, el proyecto incluye el analizador léxico, encargado de convertir cada expresión en una secuencia de tokens que posteriormente podrá ser procesada por el parser y el intérprete.

---

## 📁 Estructura del proyecto

```
Compilador-Coordenadas/
├── src/
│   ├── Token.py                    # Clase Token
│   └── AnalisiLexicoCoordenadas.py # Analizador léxico
├── docs/
│   └── Pseudocodigo.txt            # Pseudocódigo del tokenizador
└── imagenes/                       # Diagramas de los autómatas
```

## Comandos del lenguaje

### Validación de coordenadas

Determina si una coordenada es válida según sus rangos geográficos:

```text
validacion(latitud, longitud)
```

- La `latitud` debe estar entre `-90.0` y `90.0`.
- La `longitud` debe estar entre `-180.0` y `180.0`.

Ejemplos:

```text
validacion(4.7110, -74.0721)   # Coordenada válida
validacion(95.0, -74.0721)      # Coordenada inválida
```

### Consulta de coordenada

Muestra el lugar correspondiente a una coordenada:

```text
coordenada(latitud, longitud)
```

Ejemplo:

```text
coordenada(4.7110, -74.0721)
```

### Distancia entre coordenadas

Calcula la distancia entre dos coordenadas geográficas:

```text
distancia(latitud1, longitud1), (latitud2, longitud2)
```

Ejemplo:

```text
distancia(4.7110, -74.0721), (6.2442, -75.5812)
```

### Hemisferio de una coordenada

Indica el hemisferio o los hemisferios en los que se encuentran las coordenadas ingresadas:

```text
hemisferio(latitud, longitud), (latitud, longitud)
```

Ejemplo:

```text
hemisferio(4.7110, -74.0721), (6.2442, -75.5812)
```

### Búsqueda por ubicación

Obtiene las coordenadas asociadas a un lugar escrito como texto:

```text
ubicacion('String')
```

Ejemplo:

```text
ubicacion('Colombia')
```

## Autómatas

Los diagramas representan las reglas léxicas y sintácticas consideradas para cada instrucción:

| Instrucción | Autómata |
|-------------|----------|
| Validación | ![Autómata de validación](imagenes/Diagrama%20automata%20%20validaci%C3%B3n.png) |
| Coordenada | ![Autómata de coordenada](imagenes/Diagrama%20automata%20coordenada.png) |
| Distancia | ![Autómata de distancia](imagenes/Diagrama%20automata%20distancia.png) |
| Hemisferio | ![Autómata de hemisferio](imagenes/Diagrama%20automata%20hemisferio.png) |
| Ubicación | ![Autómata de ubicación](imagenes/Diagrama%20automata%20%20ubicacion.png) |

## Ejecución actual

### Requisitos
- Python 3.x (sin dependencias externas)

### Ejecución del analizador léxico

```bash
python src/AnalisiLexicoCoordenadas.py
```

El programa solicita una expresión por consola y muestra los tokens reconocidos. Ejemplo de entrada:

```
coordenada(45.12, -19.43)
```

## Tokens reconocidos

| Token          | Descripción                          | Ejemplo         |
|----------------|--------------------------------------|-----------------|
| `IDENTIFICADOR` | Palabra clave del lenguaje       | `coordenada`    |
| `STRING`        | Texto alfabético                  | `Colombia`      |
| `NUMERO`        | Número positivo entero o decimal | `45.12`         |
| `NEGATIVO`      | Número negativo                   | `-19.43`        |
| `LPARENT`       | Paréntesis izquierdo              | `(`             |
| `RPARENT`       | Paréntesis derecho                | `)`             |
| `COMA`          | Separador de argumentos           | `,`             |
| `COMILLA`       | Comilla simple                    | `'`             |

### Palabras clave

```
coordenada | ubicacion | distancia | hemisferio | validar
```

## Estado del proyecto

- [x] Diseño de autómatas para las instrucciones del lenguaje.
- [x] Analizador léxico inicial.
- [ ] Parser para validar la estructura completa de cada comando.
- [ ] Validación de rangos de latitud y longitud.
- [ ] Cálculo de distancias y detección de hemisferios.
- [ ] Consulta de lugares y coordenadas.

## Autora

Proyecto desarrollado como parte de la formación en Ingeniería de Sistemas – UPTC.
