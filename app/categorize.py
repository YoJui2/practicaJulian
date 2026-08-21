"""
Script principal de categorización.

Orquesta todo el flujo:
1. Carga las preguntas sin categorizar de la BD
2. Para cada pregunta, la clasifica con la IA
3. Si el score >= threshold → guarda automáticamente
4. Si el score < threshold → pide revisión humana
5. Guarda el resultado en la tabla categorizations
"""

from tqdm import tqdm

from app.categories import CATEGORIES, get_category_names
from app.classifier import AIClassifier
from app.database import SessionLocal
from app.human_review import (
    ask_human_for_category,
    confirm_ai_suggestion,
    display_question_context,
)
from app.models import Categorization, Question


# Umbral de confianza (70%)
CONFIDENCE_THRESHOLD = 0.70


def get_uncategorized_questions(db) -> list:
    """
    Obtiene todas las preguntas que aún no tienen una categorización.
    """
    categorized_question_ids = db.query(Categorization.question_id).subquery()
    return db.query(Question).filter(~Question.id.in_(categorized_question_ids)).all()


def save_categorization(
    db,
    question_id: int,
    category_name: str,
    confidence_score: float,
    is_automatic: bool,
) -> None:
    """
    Guarda una categorización en la base de datos.
    """
    try:
        categorization = Categorization(
            question_id=question_id,
            category_name=category_name,
            confidence_score=float(confidence_score),
            is_automatic=is_automatic,
        )
        db.add(categorization)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise RuntimeError(f"No se pudo guardar la categorización: {exc}") from exc


def categorize_all(batch_size: int = 32, threshold: float = CONFIDENCE_THRESHOLD) -> None:
    """
    Función principal que ejecuta el flujo completo de categorización.
    """
    db = SessionLocal()
    try:
        categories = CATEGORIES
        category_names = get_category_names()
        classifier = AIClassifier()

        pending_questions = get_uncategorized_questions(db)

        print("Resumen inicial")
        print(f"  - Preguntas pendientes: {len(pending_questions)}")
        print(f"  - Categorías disponibles: {len(categories)}")
        print(f"  - Umbral de confianza: {threshold:.0%}")

        processed_count = 0
        automatic_count = 0
        manual_count = 0
        skipped_count = 0

        for start_index in range(0, len(pending_questions), batch_size):
            batch = pending_questions[start_index:start_index + batch_size]

            for question in tqdm(
                batch,
                total=len(batch),
                desc=f"Procesando lote {start_index // batch_size + 1}",
            ):
                if not question.question:
                    continue

                result = classifier.classify(question.question, category_names)

                if result.confidence_score >= threshold:
                    save_categorization(
                        db,
                        question.id,
                        result.category_name,
                        result.confidence_score,
                        is_automatic=True,
                    )
                    automatic_count += 1
                else:
                    display_question_context(
                        question.question,
                        result.category_name,
                        result.confidence_score,
                        result.all_scores,
                    )

                    accepted = confirm_ai_suggestion(
                        result.category_name,
                        result.confidence_score,
                    )

                    if accepted:
                        save_categorization(
                            db,
                            question.id,
                            result.category_name,
                            result.confidence_score,
                            is_automatic=False,
                        )
                        manual_count += 1
                    else:
                        chosen_category = ask_human_for_category(categories)

                        if chosen_category is None:
                            skipped_count += 1
                            continue

                        save_categorization(
                            db,
                            question.id,
                            chosen_category,
                            result.confidence_score,
                            is_automatic=False,
                        )
                        manual_count += 1

                processed_count += 1

        print()
        print("Resumen final")
        print(f"  - Total procesadas: {processed_count}")
        print(f"  - Automáticas: {automatic_count}")
        print(f"  - Manuales: {manual_count}")
        print(f"  - Skip: {skipped_count}")

    finally:
        db.close()


if __name__ == "__main__":
    categorize_all()