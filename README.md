# Librería de Coordenadas Geográficas

Proyecto académico desarrollado para la asignatura de **Lenguajes Formales y Compiladores** de la UPTC.

El objetivo es construir una librería y un lenguaje de dominio específico (DSL) para trabajar con coordenadas geográficas. Las instrucciones permitirán validar coordenadas, consultar lugares, calcular distancias, identificar hemisferios y obtener coordenadas a partir de una ubicación.

Actualmente, el proyecto incluye el analizador léxico, encargado de convertir cada expresión en una secuencia de tokens que posteriormente podrá ser procesada por el parser y el intérprete.

---

## 📁 Estructura del proyecto

```
Compilador-Coordenadas/
├── src/
│   ├── Token.py                    # Clase Token (tipo, valor)
│   ├── AnalisiLexicoCoordenadas.py # Analizador léxico
│   ├── AnalisisSintactico.py       # Motor del Parser y búsqueda de reglas
│   ├── ReglasSintacticas.py        # Funciones que ejecutan las reglas sintácticas
│   ├── main.py                     # Punto de entrada principal
│   └── persistencia/
│       └── reglas.json             # Reglas sintácticas configuradas en JSON
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

---

## 📐 Especificación Sintáctica (Gramática EBNF / BNF)

La estructura sintáctica de las instrucciones del lenguaje se define formalmente mediante la siguiente Gramática Libre de Contexto en notación **EBNF**:

```ebnf
(* Símbolo inicial: una instrucción del lenguaje *)
<instruccion>     ::= <cmd_coordenada>
                    | <cmd_validacion>
                    | <cmd_distancia>
                    | <cmd_hemisferio>
                    | <cmd_ubicacion>

(* Componente modular para coordenadas geográficas *)
<coordenada>      ::= LPARENT <valor_numero> COMA <valor_numero> RPARENT

(* Producciones para cada comando *)
<cmd_coordenada>  ::= "coordenada" <coordenada>
<cmd_validacion>  ::= ("validacion" | "validar") <coordenada>
<cmd_distancia>   ::= "distancia" <coordenada> COMA <coordenada>
<cmd_hemisferio>  ::= "hemisferio" <coordenada> [ COMA <coordenada> ]
<cmd_ubicacion>   ::= "ubicacion" LPARENT [ COMILLA ] STRING [ COMILLA ] RPARENT

(* Valores numéricos permitidos *)
<valor_numero>    ::= NUMERO | NEGATIVO
```

### Descripción de Componentes Sintácticos

* **`<instruccion>`**: Regla inicial que deriva en cualquiera de los comandos válidos del lenguaje.
* **`<coordenada>`**: Par ordenado de la forma `(latitud, longitud)`, delimitado por paréntesis y separado por coma.
* **`<cmd_coordenada>` / `<cmd_validacion>`**: Requieren exactamente una coordenada como argumento.
* **`<cmd_distancia>`**: Requiere dos pares de coordenadas separados por una coma.
* **`<cmd_hemisferio>`**: Acepta una o dos coordenadas geográficas.
* **`<cmd_ubicacion>`**: Recibe un nombre de lugar en formato de texto (`STRING`).

### 📋 Reglas Sintácticas del Lenguaje

* **Regla General**: Toda instrucción debe iniciar con una palabra reservada válida (`coordenada`, `validacion`, `distancia`, `hemisferio` o `ubicacion`) y continuar con la estructura de argumentos correspondiente a dicha función.
* **Regla de Coordenada**: Una coordenada está compuesta obligatoriamente por:
  1. Paréntesis de apertura `(`
  2. Un valor numérico (`latitud`)
  3. Una coma `,`
  4. Un valor numérico (`longitud`)
  5. Paréntesis de cierre `)`
* **Regla de Consulta de Coordenada y Validación**:
  * Inicia con la palabra clave `coordenada` o `validacion` / `validar`.
  * Sigue exactamente una `<coordenada>`.
  * *Ejemplo*: `coordenada(4.7110, -74.0721)`
* **Regla de Distancia**:
  * Inicia con la palabra clave `distancia`.
  * Sigue una primera `<coordenada>`.
  * Sigue una coma separadora `,`.
  * Sigue una segunda `<coordenada>`.
  * *Ejemplo*: `distancia(4.7110, -74.0721), (6.2442, -75.5812)`
* **Regla de Hemisferio**:
  * Inicia con la palabra clave `hemisferio`.
  * Sigue una primera `<coordenada>`.
  * Opcionalmente, puede incluir una coma `,` y una segunda `<coordenada>`.
  * *Ejemplo*: `hemisferio(4.7110, -74.0721)` o `hemisferio(4.71, -74.07), (6.24, -75.58)`
* **Regla de Búsqueda por Ubicación**:
  * Inicia con la palabra clave `ubicacion`.
  * Sigue un paréntesis de apertura `(`.
  * Sigue un token de texto `STRING` (opcionalmente delimitado por comillas según el lexer).
  * Sigue un paréntesis de cierre `)`.
  * *Ejemplo*: `ubicacion('Colombia')`


---

## Autómatas

Los diagramas representan las reglas léxicas y sintácticas consideradas para cada instrucción:

| Instrucción | Autómata |
|-------------|----------|
| Validación | ![Autómata de validación](imagenes/Diagrama%20automata%20%20validaci%C3%B3n.png) |
| Coordenada | ![Autómata de coordenada](imagenes/Diagrama%20automata%20coordenada.png) |
| Distancia | ![Autómata de distancia](imagenes/Diagrama%20automata%20distancia.png) |
| Hemisferio | ![Autómata de hemisferio](imagenes/Diagrama%20automata%20hemisferio.png) |
| Ubicación | ![Autómata de ubicación](imagenes/Diagrama%20automata%20%20ubicacion.png) |

## 🔄 Arquitectura y Flujo del Análisis Sintáctico

El compilador utiliza un enfoque modular donde la entrada de usuario se tokeniza en la fase léxica y se procesa mediante un motor de análisis sintáctico desacoplado, configurado a través de `persistencia/reglas.json` y ejecutado por `ReglasSintacticas.py`:

![Diagrama del Analizador Sintáctico](imagenes/diagrama%20analizador%20sintactico.png)

### Funcionamiento paso a paso:

1. **Entrada del Usuario (`main.py`)**:
   - El programa solicita al usuario la instrucción o expresión geográfica (ej. `coordenada[4.7110, -74.0721]`).
   - `main.py` actúa como orquestador principal, capturando la entrada y enviándola a las fases de análisis.

2. **Análisis Léxico (`AnalisiLexicoCoordenadas.py`)**:
   - La función `tokenizar(texto)` escanea la cadena carácter a carácter.
   - Clasifica y genera una lista ordenada de objetos `Token` reconociendo palabras clave (`IDENTIFICADOR`), texto libre (`STRING`), delimitadores (`LPARENT`, `RPARENT`), números con signo (`NUMERO`, `NEGATIVO`), comas (`COMA`) y comillas (`COMILLA`).
   - Descarta espacios en blanco y detecta errores léxicos ante caracteres no reconocidos.

3. **Carga y Búsqueda de Reglas (`AnalisisSintactico.py` + `reglas.json`)**:
   - Se crea una instancia de la clase `parser(tokens)`.
   - El método `_cargar_reglas()` lee el archivo de configuración `persistencia/reglas.json`.
   - Con `buscar_regla()`, el parser inspecciona el primer token (`IDENTIFICADOR`) y obtiene la configuración de funciones requeridas para esa instrucción (`funcion_clave` y `funcion_argumentos`).

4. **Validación Sintáctica Dinámica (`ReglasSintacticas.py`)**:
   - El parser invoca dinámicamente mediante `ejecucion_metodo(nombre_metodo)` las funciones correspondientes usando `getattr()`:
     - **Validación del comando**: Ejecuta `revisar_palabra_clave(parser)` para asegurar y consumir el comando inicial.
     - **Validación de argumentos**: Ejecuta la función asociada (`revisar_validacion_coordenada`, `regla_distancia`, `regla_ubicacion`), la cual consume secuencialmente los tokens esperados (`LPARENT`, `NUMERO`/`NEGATIVO`/`STRING`, `COMA`, `RPARENT`) avanzando el puntero `parser.pos` y verificando la gramática.

5. **Construcción y Retorno del Resultado**:
   - El método `analizador()` empaqueta la información procesada en un diccionario estructurado:
     ```python
     {
         "comando": comando,
         "argumentos": argumentos  # ej: (4.7110, -74.0721) o ((lat1, lon1), (lat2, lon2))
     }
     ```
   - El resultado es devuelto a `main.py` para su visualización o posterior procesamiento.

---

## Ejecución del proyecto

### Requisitos
- Python 3.x (sin dependencias externas)

### Ejecución del compilador completo:

```bash
python src/main.py
```

Ejemplo de ejecución interactiva:
```text
Ingrese la información: coordenada[4.7110, -74.0721]
Tokens generados: [Token(IDENTIFICADOR, 'coordenada'), Token(LPARENT, '['), Token(NUMERO, 4.711), Token(COMA, ','), Token(NEGATIVO, -74.0721), Token(RPARENT, ']')]
Resultado del análisis sintáctico: {'comando': 'coordenada', 'argumentos': (4.711, -74.0721)}
```

### Ejecución exclusiva del analizador léxico:

```bash
python src/AnalisiLexicoCoordenadas.py
```

## Tokens reconocidos

| Token          | Descripción                              | Ejemplo         |
|----------------|------------------------------------------|-----------------|
| `IDENTIFICADOR` | Palabra clave reservada del lenguaje     | `coordenada`    |
| `STRING`        | Texto alfabético                          | `Colombia`      |
| `NUMERO`        | Número positivo entero o decimal         | `45.12`         |
| `NEGATIVO`      | Número negativo entero o decimal         | `-19.43`        |
| `LPARENT`       | Delimitador de apertura corchete `[`     | `[`             |
| `RPARENT`       | Delimitador de cierre corchete `]`       | `]`             |
| `COMA`          | Separador de argumentos `,`              | `,`             |
| `COMILLA`       | Delimitador de comilla simple `'`        | `'`             |

### Palabras clave

```
coordenada | ubicacion | distancia | hemisferio | validar
```

## Estado del proyecto

- [x] Diseño de autómatas para las instrucciones del lenguaje.
- [x] Analizador léxico inicial.
- [x] Motor de Parser con carga de reglas JSON e invocación dinámica (`AnalisisSintactico.py` y `ReglasSintacticas.py`).
- [ ] Validación sintáctica del resto de comandos (`distancia`, `hemisferio`, `ubicacion`, `validar`).
- [ ] Validación semántica de rangos de latitud y longitud.
- [ ] Cálculo de distancias y detección de hemisferios.
- [ ] Consulta de lugares y coordenadas.

## Autora

Proyecto desarrollado como parte de la formación en Ingeniería de Sistemas – UPTC.
