# Testing del proyecto

## Resumen

Se incorporó una suite de pruebas con `pytest` para comprobar cuatro áreas del proyecto:

- Tests unitarios.
- Calidad de datos.
- Integración entre FastAPI y SQLAlchemy.
- Validación de entradas HTTP.

La suite actual contiene **32 tests**.

## Cambios realizados

### Configuración de pytest

En `pyproject.toml` se agregaron:

- `pytest` como dependencia de desarrollo.
- `testpaths = ["tests"]` para indicar dónde buscar los tests.
- `pythonpath = ["."]` para permitir imports como `from app...`.

Los tests deben ejecutarse con el entorno virtual del proyecto:

```powershell
.\.venv\Scripts\pytest.exe -q
```

También es posible ejecutar una categoría concreta:

```powershell
.\.venv\Scripts\pytest.exe -q tests\unit
.\.venv\Scripts\pytest.exe -q tests\test_data_quality.py
.\.venv\Scripts\pytest.exe -q tests\test_integration.py
.\.venv\Scripts\pytest.exe -q tests\test_validation.py
```

## Estructura de tests

```text
tests/
    conftest.py
    test_data_quality.py
    test_integration.py
    test_validation.py
    unit/
        test_categories.py
        test_classifier.py
        test_categorize.py
        test_human_review.py
```

## Tests unitarios

Los tests unitarios verifican funciones aisladas sin acceder a servicios externos.

### `test_categories.py`

Comprueba:

- Obtención de nombres, labels y descripciones.
- Búsqueda de una categoría existente.
- Resultado `None` cuando la categoría no existe.

### `test_classifier.py`

El pipeline de Hugging Face se reemplaza por un mock. Se comprueba:

- Inicialización del clasificador sin descargar un modelo real.
- Conversión de labels y scores a `ClassificationResult`.
- Clasificación de varios textos mediante `classify_batch()`.

### `test_human_review.py`

La función `input()` se reemplaza con `monkeypatch`. Se comprueba:

- Selección de una categoría válida.
- Reintento después de una opción inválida.
- Opción `Skip`.
- Aceptación, rechazo y respuesta desconocida ante una sugerencia de IA.

### `test_categorize.py`

Se utiliza una sesión simulada con `MagicMock`. Se comprueba:

- Guardado y confirmación mediante `commit()`.
- Rollback y conversión de errores a `RuntimeError`.
- Consulta de preguntas sin categorizar.

## Tests de calidad de datos

Archivo: `tests/test_data_quality.py`

Se comprueba el procesamiento de filas provenientes de SimpleQA:

- Metadata en formato JSON.
- Metadata como literal de Python.
- Metadata inválida o vacía.
- Limpieza de espacios en preguntas y respuestas.
- Uso de `problem` y del alias `question`.
- Descarte de filas sin pregunta o respuesta.
- Extracción de `topic` como categoría.
- Extracción de la primera URL como fuente.
- Límites de 100 caracteres para categoría y 255 para fuente.

Durante estos tests se detectó y corrigió un error en `app/load_data.py`: la función efectiva `simpleqa_row_to_fields()` siempre devolvía `source=None`, aunque la metadata tuviera URLs. Ahora conserva la primera URL válida, limpia sus espacios y aplica el límite de 255 caracteres.

## Tests de integración

Archivo: `tests/test_integration.py`

La fixture de `tests/conftest.py` configura:

- SQLite en memoria.
- `StaticPool` para compartir la misma base durante cada test.
- Tablas SQLAlchemy temporales.
- Override de la dependencia `get_db` de FastAPI.
- Limpieza de tablas y engine al finalizar cada test.

Se comprueba el flujo completo de la API:

- Crear una pregunta con `POST /questions`.
- Listar preguntas.
- Consultar una pregunta por ID.
- Obtener estadísticas generales.
- Filtrar por categoría categorizada.
- Obtener estadísticas de categorización automática y manual.

Estos tests no necesitan PostgreSQL ni modificar datos reales.

## Tests de validación

Archivo: `tests/test_validation.py`

Se comprueba que la API responde `422` ante:

- Campos obligatorios ausentes.
- Pregunta o respuesta vacías.
- Tipos incorrectos.
- Categorías de más de 100 caracteres.
- Fuentes de más de 255 caracteres.

También se comprueba:

- Creación correcta con un payload válido.
- Respuesta actual para una pregunta inexistente.

La API actualmente devuelve `200` y `{ "error": "Pregunta no encontrada" }` cuando no existe la pregunta. El test documenta ese comportamiento actual.

## Resultado verificado

La ejecución completa realizada con el entorno virtual produjo:

```text
32 passed, 2 warnings
```

Los warnings provienen del uso de `@app.on_event("startup")`, que FastAPI marca como obsoleto en favor de los lifespan events. No impiden la ejecución de los tests.

## Dependencias externas aisladas

La suite no requiere:

- Descargar el modelo de Hugging Face.
- Acceder a Internet.
- Ejecutar PostgreSQL.
- Introducir datos manualmente por consola.
- Cargar el dataset real desde Hugging Face.
