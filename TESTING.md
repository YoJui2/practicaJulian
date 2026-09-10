# Pruebas del proyecto

## Resumen

El proyecto usa `pytest` para comprobar cuatro tipos de pruebas:

- **Unitarias:** revisan una función pequeña de forma aislada.
- **Calidad de datos:** revisan cómo se limpian y preparan los datos importados.
- **Integración:** revisan varias partes juntas, por ejemplo la API y la base de datos.
- **Validación:** revisan qué ocurre cuando una petición tiene datos incorrectos.

Cada prueba intenta comprobar una sola idea. Por eso los ejemplos son intencionadamente pequeños y fáciles de leer.

## Ejecutar las pruebas

Desde la carpeta principal del proyecto:

```powershell
poetry run pytest -q
```

También se puede ejecutar un grupo:

```powershell
poetry run pytest -q tests/unit
poetry run pytest -q tests/test_data_quality.py
poetry run pytest -q tests/test_integration.py
poetry run pytest -q tests/test_validation.py
```

La opción `-q` muestra un resumen corto.

## Organización

```text
tests/
    conftest.py
    test_data_quality.py
    test_integration.py
    test_validation.py
    unit/
        test_categories.py
        test_categorize.py
        test_human_review.py
```

## 1. Pruebas unitarias

Archivos: `tests/unit/`

Comprueban funciones pequeñas sin levantar la API completa:

- `test_categories.py` comprueba la lista de categorías y la búsqueda de una categoría.
- `test_categorize.py` comprueba que una categorización se guarda y que un error provoca una recuperación correcta.
- `test_human_review.py` comprueba una elección válida, la opción de saltar y la confirmación de una sugerencia.

Cada una usa datos cortos, como una pregunta y una categoría, para que sea sencillo ver qué se espera.

## 2. Pruebas de calidad de datos

Archivo: `tests/test_data_quality.py`

Comprueban que una fila importada se puede usar en la aplicación:

- Lee metadata sencilla.
- Devuelve un diccionario vacío si la metadata no es válida.
- Limpia espacios de una pregunta y su respuesta.
- Descarta una fila sin respuesta.
- Respeta los límites de longitud de categoría y fuente.

## 3. Pruebas de integración

Archivo: `tests/test_integration.py`

Comprueba el recorrido principal de una pregunta en la API:

1. Crear una pregunta.
2. Consultar la pregunta creada.
3. Listar las preguntas.
4. Consultar las estadísticas.

La fixture de `tests/conftest.py` usa una base SQLite temporal. Los datos se borran al terminar cada prueba, así que no se modifica la base real.

## 4. Pruebas de validación

Archivo: `tests/test_validation.py`

Comprueban que la API rechaza datos incorrectos:

- Falta la pregunta o la respuesta.
- La categoría supera los 100 caracteres.
- Se envía un número donde debe ir texto.
- La API acepta una petición válida.
- La API devuelve un mensaje cuando se busca una pregunta inexistente.

## Resultado esperado

Al ejecutar toda la suite debe aparecer un resumen similar a:

```text
23 passed
```

El número puede cambiar si se agregan nuevas pruebas.

## Dependencias aisladas

Las pruebas no necesitan:

- Descargar el modelo de Hugging Face.
- Acceder a Internet.
- Ejecutar PostgreSQL.
- Cargar el dataset real desde Hugging Face.
