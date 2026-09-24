"""
Definición centralizada de las categorías disponibles para clasificación.

Cada categoría tiene:
- name: identificador interno (snake_case)
       "description": "Preguntas sobre historia, eventos históricos, guerras, civilizaciones, personajes históricos, fechas importantes y hechos del pasado.",
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

CATEGORIES: list[dict[str, str]] = [
    {
        "name": "historia",
        "label": "Historia",
        "description": "Preguntas sobre historia, eventos históricos, guerras, civilizaciones, personajes históricos, fechas importantes y hechos del pasado.",
    },
    {
        "name": "deportes",
        "label": "Deportes",
        "description": "Preguntas sobre deportes, atletas, equipos, competiciones, récords, reglas deportivas y eventos deportivos.",
    },
    {
        "name": "geografia",
        "label": "Geografía",
        "description": "Preguntas sobre países, ciudades, capitales, ríos, montañas, continentes, mapas, demografía y lugares del mundo.",
    },
    {
        "name": "arte",
        "label": "Arte",
        "description": "Preguntas sobre pintura, escultura, arquitectura, artistas, movimientos artísticos, museos, obras famosas y expresiones culturales.",
    },
    {
        "name": "ciencia",
        "label": "Ciencia",
        "description": "Preguntas sobre física, química, biología, medicina, astronomía, naturaleza, tecnología, inventos y descubrimientos científicos.",
    },
    {
        "name": "entretenimiento",
        "label": "Entretenimiento",
        "description": "Preguntas sobre cine, televisión, música, videojuegos, celebridades, personajes, programas y cultura popular.",
    },
]


def get_category_names() -> list[str]:
    """Retorna una lista con los nombres (name) de todas las categorías."""
    return [category["name"] for category in CATEGORIES]


def get_category_labels() -> list[str]:
    """Retorna una lista con los labels legibles de todas las categorías."""
    return [category["label"] for category in CATEGORIES]


def get_category_descriptions() -> list[str]:
    """Retorna una lista con las descripciones de todas las categorías."""
    return [category["description"] for category in CATEGORIES]


def find_category_by_name(name: str) -> dict | None:
    """Busca y retorna una categoría por su nombre. Retorna None si no existe."""
    return next((category for category in CATEGORIES if category["name"] == name), None)
