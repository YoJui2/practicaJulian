"""
Script principal de traducción.

Orquesta todo el flujo:
1. Carga las preguntas sin traducir de la BD
2. Para cada pregunta, traduce la pregunta y su respuesta con IA
3. Guarda el resultado en la tabla translations
"""

import argparse

from tqdm import tqdm

from app.database import SessionLocal
from app.models import Question, Translation
from app.translator import DEFAULT_TARGET_LANG, translate_text


def get_untranslated_questions(db, target_lang: str) -> list:
    """
    Obtiene las preguntas que aún no tienen una traducción al idioma pedido.
    """
    translated_question_ids = db.query(Translation.question_id).filter(
        Translation.lang == target_lang
    ).subquery()
    return (
        db.query(Question)
        .filter(~Question.id.in_(translated_question_ids))
        .all()
    )


def save_translation(
    db,
    question_id: int,
    lang: str,
    question_translated: str,
    answer_translated: str,
    is_automatic: bool = True,
) -> None:
    """
    Guarda una traducción en la base de datos.
    """
    try:
        translation = Translation(
            question_id=question_id,
            lang=lang,
            question_translated=question_translated,
            answer_translated=answer_translated,
            is_automatic=is_automatic,
        )
        db.add(translation)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise RuntimeError(f"No se pudo guardar la traducción: {exc}") from exc


def translate_all(
    max_questions: int | None = None,
    target_lang: str = DEFAULT_TARGET_LANG,
) -> None:
    """
    Traduce todas las pendientes o una tanda limitada.
    """
    db = SessionLocal()
    try:
        pending_questions = get_untranslated_questions(db, target_lang)
        if max_questions is not None:
            pending_questions = pending_questions[:max_questions]

        print("Resumen inicial")
        print(f"  - Preguntas pendientes: {len(pending_questions)}")
        print(f"  - Idioma de destino: {target_lang}")

        translated_count = 0
        skipped_count = 0

        for question in tqdm(
            pending_questions,
            total=len(pending_questions),
            desc="Traduciendo preguntas",
        ):
            if not question.question or not question.answer:
                skipped_count += 1
                continue

            question_translated = translate_text(question.question)
            answer_translated = translate_text(question.answer)

            save_translation(
                db,
                question.id,
                target_lang,
                question_translated,
                answer_translated,
                is_automatic=True,
            )
            translated_count += 1

        print()
        print("Resumen final")
        print(f"  - Total procesadas: {translated_count}")
        print(f"  - Skip: {skipped_count}")

    finally:
        db.close()


def translate_100() -> None:
    """Traduce hasta 100 preguntas pendientes."""
    translate_all(max_questions=100)


def translate_250() -> None:
    """Traduce hasta 250 preguntas pendientes."""
    translate_all(max_questions=250)


def translate_500() -> None:
    """Traduce hasta 500 preguntas pendientes."""
    translate_all(max_questions=500)


def main() -> None:
    parser = argparse.ArgumentParser(description="Traduce preguntas pendientes")
    parser.add_argument(
        "--limit",
        type=int,
        choices=(100, 250, 500),
        help="cantidad máxima de preguntas a traducir en esta ejecución",
    )
    args = parser.parse_args()

    translate_all(max_questions=args.limit)


if __name__ == "__main__":
    main()