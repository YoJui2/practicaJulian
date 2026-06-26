"""
Definición centralizada de las categorías disponibles para clasificación.

Cada categoría tiene:
- name: identificador interno (snake_case)
- label: nombre legible para mostrar al usuario
- description: texto que la IA usa para entender el significado de la categoría

TAREA: Definí al menos 6 categorías relevantes para el dataset de preguntas.
       Pensá en categorías que sean mutuamente excluyentes y que cubran
       la mayor cantidad posible de preguntas.

Ejemplo de estructura:

CATEGORIES = [
    {
        "name": "machine_learning",
        "label": "Machine Learning",
        "description": "Preguntas sobre algoritmos de aprendizaje automático, redes neuronales, overfitting, gradient descent, etc."
    },
    {
        "name": "historia",
        "label": "Historia",
        "description": "Preguntas sobre eventos históricos, personajes, guerras, civilizaciones, etc."
    },
    # ... más categorías
]
"""

# TODO: Implementar la lista CATEGORIES con al menos 6 categorías.
#       Cada categoría debe ser un diccionario con las claves: "name", "label", "description".
#       Las descripciones deben ser claras y detalladas para que la IA pueda usarlas
#       como referencia al momento de clasificar.

CATEGORIES: list[dict[str, str]] = []


def get_category_names() -> list[str]:
    """Retorna una lista con los nombres (name) de todas las categorías."""
    # TODO: Implementar. Debe retornar algo como ["machine_learning", "historia", ...]
    pass


def get_category_labels() -> list[str]:
    """Retorna una lista con los labels legibles de todas las categorías."""
    # TODO: Implementar.
    pass


def get_category_descriptions() -> list[str]:
    """Retorna una lista con las descripciones de todas las categorías."""
    # TODO: Implementar.
    pass


def find_category_by_name(name: str) -> dict | None:
    """Busca y retorna una categoría por su nombre. Retorna None si no existe."""
    # TODO: Implementar.
    pass