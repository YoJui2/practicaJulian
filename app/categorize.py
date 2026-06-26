"""
Script principal de categorización.

Orquesta todo el flujo:
1. Carga las preguntas sin categorizar de la BD
2. Para cada pregunta, la clasifica con la IA
3. Si el score >= threshold → guarda automáticamente
4. Si el score < threshold → pide revisión humana
5. Guarda el resultado en la tabla categorizations

TAREA: Implementar la función principal y las funciones auxiliares.
"""
from tqdm import tqdm


# Umbral de confianza (70%)
CONFIDENCE_THRESHOLD = 0.70


def get_uncategorized_questions(db) -> list:
    """
    Obtiene todas las preguntas que aún no tienen una categorización.

    Args:
        db: sesión de SQLAlchemy

    Returns:
        Lista de objetos Question que no tienen una entrada en la tabla categorizations.

    TODO:
    - Hacer una query que obtenga preguntas cuyo id NO esté en la tabla categorizations
    - Pista: usá .filter(~Question.id.in_(subquery)) o un LEFT JOIN con filtro IS NULL
    - Retornar la lista de preguntas
    """
    # TODO: Implementar
    pass


def save_categorization(db, question_id: int, category_name: str, confidence_score: float, is_automatic: bool) -> None:
    """
    Guarda una categorización en la base de datos.

    Args:
        db: sesión de SQLAlchemy
        question_id: ID de la pregunta categorizada
        category_name: nombre de la categoría asignada
        confidence_score: score de confianza de la IA
        is_automatic: True si fue decisión automática, False si fue humana

    TODO:
    - Crear una instancia de Categorization con los datos recibidos
    - Agregarla a la sesión con db.add()
    - Hacer db.commit()
    - Manejar excepciones con try/except y hacer db.rollback() si falla
    """
    # TODO: Implementar
    pass


def categorize_all(batch_size: int = 32, threshold: float = CONFIDENCE_THRESHOLD) -> None:
    """
    Función principal que ejecuta el flujo completo de categorización.

    Args:
        batch_size: tamaño del lote para procesamiento
        threshold: umbral de confianza para decisión automática

    TODO:
    1. Obtener una sesión de BD (usar SessionLocal o get_db)
    2. Cargar las categorías desde app/categories.py
    3. Instanciar el clasificador (AIClassifier)
    4. Obtener las preguntas sin categorizar
    5. Mostrar resumen inicial:
       - Total de preguntas pendientes
       - Categorías disponibles
       - Umbral de confianza
    6. Iterar sobre las preguntas (usar tqdm para progreso):
       a. Clasificar la pregunta con el clasificador
       b. Si score >= threshold:
          - Guardar como automática
          - Incrementar contador de automáticas
       c. Si score < threshold:
          - Mostrar contexto al humano (display_question_context)
          - Preguntar si acepta la sugerencia (confirm_ai_suggestion)
          - Si acepta → guardar con la sugerencia
          - Si no acepta → pedir categoría manual (ask_human_for_category)
          - Si elige skip → continuar sin guardar
          - Incrementar contador de manuales
    7. Mostrar resumen final:
       - Total procesadas
       - Automáticas vs manuales
       - Skipped
    """
    # TODO: Implementar
    pass


if __name__ == "__main__":
    categorize_all()