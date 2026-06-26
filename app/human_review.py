"""
Módulo de revisión humana por consola.

Cuando la IA no tiene suficiente confianza (score < threshold),
este módulo le pregunta al usuario por terminal qué categoría corresponde.

TAREA: Implementar las funciones de interacción por consola.
"""


def display_question_context(question_text: str, ai_suggestion: str, confidence: float, all_scores: dict[str, float]) -> None:
    """
    Muestra al usuario la pregunta, la sugerencia de la IA, y los scores.

    Debe imprimir algo como:

    ════════════════════════════════════════════════════════════════
    REVISIÓN MANUAL REQUERIDA (confianza < 70%)
    ════════════════════════════════════════════════════════════════

    Pregunta: ¿Cuál es la velocidad de la luz en el vacío?

    Sugerencia de la IA: física (confianza: 65%)

    Scores de todas las categorías:
      1. física         → 65%
      2. astronomía     → 20%
      3. matemáticas    → 10%
      4. historia       → 5%

    ════════════════════════════════════════════════════════════════

    Args:
        question_text: texto de la pregunta
        ai_suggestion: categoría sugerida por la IA
        confidence: score de confianza (0.0 a 1.0)
        all_scores: diccionario {categoría: score}

    TODO:
    - Imprimir el encabezado visual
    - Mostrar la pregunta
    - Mostrar la sugerencia de la IA con su confianza en porcentaje
    - Mostrar los scores de todas las categorías ordenados de mayor a menor
    - Numerar las categorías (1, 2, 3, ...)
    """
    # TODO: Implementar
    pass


def ask_human_for_category(categories: list[dict[str, str]]) -> str | None:
    """
    Le pide al usuario que elija una categoría por consola.

    Debe mostrar las opciones numeradas y esperar input:

    Opciones:
      1. Machine Learning
      2. Historia
      3. Geografía
      ...
      S. Skip (omitir esta pregunta)

    Elegí una opción:

    Args:
        categories: lista de categorías (cada una con "name" y "label")

    Returns:
        El "name" de la categoría elegida, o None si el usuario eligió skip.

    TODO:
    - Mostrar las categorías numeradas usando su "label"
    - Agregar opción "S" para skip
    - Leer input del usuario con input()
    - Validar que la entrada sea un número válido o "S"/"s"
    - Si la entrada es inválida, volver a preguntar (loop)
    - Retornar el "name" de la categoría elegida o None si skip
    """
    # TODO: Implementar
    pass


def confirm_ai_suggestion(ai_suggestion: str, confidence: float) -> bool:
    """
    Pregunta al usuario si acepta la sugerencia de la IA.

    ¿Aceptás la sugerencia "machine_learning" (65%)? [S/n]:

    Args:
        ai_suggestion: categoría sugerida por la IA
        confidence: score de confianza

    Returns:
        True si el usuario acepta, False si no.

    TODO:
    - Mostrar la pregunta de confirmación
    - Leer input del usuario
    - Interpretar respuesta vacía o "S"/"s" como True
    - Interpretar "N"/"n" como False
    """
    # TODO: Implementar
    pass