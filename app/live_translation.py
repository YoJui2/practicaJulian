"""Traducción en vivo de una pregunta y sus opciones.

Cuando el juego elige una pregunta, este módulo arma las opciones en el idioma
original y las traduce al español en el momento, sin guardar nada en la base.
La versión con tabla de traducciones reutiliza este mismo servicio como fuente.
"""

from app.options import build_options
from app.translator import (
    DEFAULT_SOURCE_LANG,
    DEFAULT_TARGET_LANG,
    translate_texts,
)


def build_english_options(question: str, answer: str) -> list[str]:
    """Genera las opciones en el idioma original de la pregunta."""
    return build_options(question, answer)


def translate_question(
    question: str,
    answer: str,
    options: list[str] | None = None,
    target_lang: str = DEFAULT_TARGET_LANG,
) -> dict:
    """
    Traduce la pregunta, la respuesta y sus opciones al idioma pedido.

    Devuelve un diccionario con `question`, `answer`, `options` y `lang`.
    La respuesta traducida siempre coincide con una de las opciones para que el
    juego pueda comparar la opción elegida con la respuesta correcta.
    """
    source_options = list(options) if options else build_english_options(question, answer)

    texts = translate_texts([question, *source_options])
    translated_question = texts[0]
    translated_options = texts[1:]

    translated_answer = _match_translated_answer(
        answer,
        source_options,
        translated_options,
    )

    return {
        "question": translated_question,
        "answer": translated_answer,
        "options": translated_options,
        "lang": target_lang,
        "original": {
            "question": question,
            "answer": answer,
            "options": source_options,
            "lang": DEFAULT_SOURCE_LANG,
        },
    }


def _match_translated_answer(
    answer: str,
    source_options: list[str],
    translated_options: list[str],
) -> str:
    """
    Devuelve la traducción de la respuesta correcta.

    Busca la respuesta dentro de las opciones originales para reutilizar su
    traducción. Si no aparece, traduce el texto de la respuesta por separado.
    """
    target = " ".join(answer.strip().split()).lower()

    for index, option in enumerate(source_options):
        if " ".join(option.strip().split()).lower() == target:
            return translated_options[index]

    return translate_texts([answer])[0]
