"""
Módulo de revisión humana por consola.

Cuando la IA no tiene suficiente confianza (score < threshold),
este módulo le pregunta al usuario por terminal qué categoría corresponde.

TAREA: Implementar las funciones de interacción por consola.
"""


def display_question_context(question_text: str, ai_suggestion: str, confidence: float, all_scores: dict[str, float]) -> None:
    """
    Muestra al usuario la pregunta, la sugerencia de la IA, y los scores.
    """
    print("=" * 72)
    print("REVISIÓN MANUAL REQUERIDA (confianza < 70%)")
    print("=" * 72)
    print()
    print(f"Pregunta: {question_text}")
    print()
    print(f"Sugerencia de la IA: {ai_suggestion} (confianza: {confidence * 100:.0f}%)")
    print()
    print("Scores de todas las categorías:")
    ordered_scores = sorted(all_scores.items(), key=lambda item: item[1], reverse=True)

    for idx, (category, score) in enumerate(ordered_scores, start=1):
        print(f"  {idx}. {category:<20} → {score * 100:.0f}%")
    print()
    print("=" * 72)


def ask_human_for_category(categories: list[dict[str, str]]) -> str | None:
    """
    Le pide al usuario que elija una categoría por consola.
    """
    while True:
        print("Opciones:")
        for index, category in enumerate(categories, start=1):
            print(f"  {index}. {category['label']}")
        print("  S. Skip (omitir esta pregunta)")
        print()
        choice = input("Elegí una opción: ").strip()

        if choice.lower() == "s":
            return None

        if choice.isdigit():
            option_index = int(choice) - 1
            if 0 <= option_index < len(categories):
                return categories[option_index]["name"]

        print("Opción inválida. Intentá nuevamente.")


def confirm_ai_suggestion(ai_suggestion: str, confidence: float) -> bool:

    answer = input(
        f'¿Aceptás la sugerencia "{ai_suggestion}" ({confidence * 100:.0f}%)? [S/n]: '
    ).strip()

    if answer == "" or answer.lower() == "s":
        return True
    if answer.lower() == "n":
        return False

    return True