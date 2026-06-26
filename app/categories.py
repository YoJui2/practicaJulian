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

CATEGORIES: list[dict[str, str]] = [
    {
        "name": "science_and_technology",
        "label": "Ciencia y tecnología",
        "description": "Preguntas sobre ciencia, tecnología, ingeniería, física, química, biología, medicina, informática, astronomía, inventos, descubrimientos científicos y avances tecnológicos.",
    },
    {
        "name": "politics",
        "label": "Política",
        "description": "Preguntas sobre política, gobiernos, elecciones, partidos políticos, líderes, leyes, diplomacia, conflictos internacionales y actualidad política.",
    },
    {
        "name": "art",
        "label": "Arte",
        "description": "Preguntas sobre arte, pintura, escultura, arquitectura, artistas, movimientos artísticos, museos, obras famosas y expresiones culturales visuales.",
    },
    {
        "name": "other",
        "label": "Otros",
        "description": "Preguntas que no encajan claramente en ninguna otra categoría, temas misceláneos o de alcance general que no son específicos de un dominio concreto.",
    },
    {
        "name": "geography",
        "label": "Geografía",
        "description": "Preguntas sobre geografía, países, ciudades, capitales, ríos, montañas, continentes, mapas, demografía y lugares del mundo.",
    },
    {
        "name": "sports",
        "label": "Deportes",
        "description": "Preguntas sobre deportes, atletas, equipos, competiciones, olímpicos, récords, reglas deportivas y eventos deportivos.",
    },
    {
        "name": "music",
        "label": "Música",
        "description": "Preguntas sobre música, cantantes, bandas, compositores, álbumes, canciones, géneros musicales, instrumentos y premios musicales.",
    },
    {
        "name": "tv_shows",
        "label": "Series de TV",
        "description": "Preguntas sobre series de televisión, programas de TV, actores, personajes, temporadas, episodios y producciones televisivas.",
    },
    {
        "name": "history",
        "label": "Historia",
        "description": "Preguntas sobre historia, eventos históricos, guerras, civilizaciones, personajes históricos, fechas importantes y hechos del pasado.",
    },
    {
        "name": "video_games",
        "label": "Videojuegos",
        "description": "Preguntas sobre videojuegos, consolas, desarrolladores, personajes de juegos, sagas, mecánicas de juego y la industria del gaming.",
    },
]


def get_category_names() -> list[str]:
    """Retorna una lista con los nombres (name) de todas las categorías."""
    # TODO: Implementar. Debe retornar algo como ["machine_learning", "historia", ...]
    return [category["name"] for category in CATEGORIES]

    pass


def get_category_labels() -> list[str]:
    """Retorna una lista con los labels legibles de todas las categorías."""
    # TODO: Implementar.
    return [category["label"] for category in CATEGORIES]
    pass


def get_category_descriptions() -> list[str]:
    """Retorna una lista con las descripciones de todas las categorías."""
    # TODO: Implementar.
    return [category["description"] for category in CATEGORIES]
    pass


def find_category_by_name(name: str) -> dict | None:
    """Busca y retorna una categoría por su nombre. Retorna None si no existe."""
    # TODO: Implementar.
    return next((category for category in CATEGORIES if category["name"] == name), None)
    pass
