# Compilador de Coordenadas Geográficas

Proyecto académico desarrollado para la asignatura de **Lenguajes Formales y Compiladores** – UPTC.

Implementa un **analizador léxico (lexer)** para un lenguaje de dominio específico (DSL) orientado al manejo de coordenadas geográficas.

---

## 📁 Estructura del proyecto

```
Compilador-Coordenadas/
├── src/
│   ├── Token.py                  # Clase Token: representa cada unidad léxica
│   └── AnalisiLexicoCoordenadas.py # Analizador léxico principal
├── docs/
│   └── Pseudocodigo.txt          # Versión en pseudocódigo del tokenizador
└── imagenes/                     # Imágenes y recursos visuales del proyecto
```

---

## 🚀 Cómo ejecutar

### Requisitos
- Python 3.x (sin dependencias externas)

### Ejecución del analizador léxico

```bash
python src/AnalisiLexicoCoordenadas.py
```

El programa solicita una expresión por consola. Ejemplo de entrada:

```
coordenada(45.12, -19.43)
```

---

## 🔤 Tokens reconocidos

| Token          | Descripción                          | Ejemplo         |
|----------------|--------------------------------------|-----------------|
| IDENTIFICADOR| Palabras clave del lenguaje          | coordenada    |
| STRING       | Texto alfabético                     | 
orte         |
| NUMERO       | Número positivo (entero o decimal)   | 45.12         |
| NEGATIVO     | Número negativo                      | -19.43        |
| LPARENT      | Paréntesis izquierdo                 | (             |
| RPARENT      | Paréntesis derecho                   | )             |
| COMA         | Separador de argumentos              | ,             |
| COMILLA      | Comilla simple                       | '             |

### Palabras clave soportadas

```
coordenada  |  ubicacion  |  distancia  |  hemisferio  |  validar
```

---

## 👩‍💻 Autora

Proyecto desarrollado como parte de la formación en Ingeniería de Sistemas – UPTC.
