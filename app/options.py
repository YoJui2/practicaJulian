"""Generacion de opciones de opcion multiple a partir de la pregunta."""

import re
from random import shuffle
from typing import Callable

DISTRACTOR_COUNT = 3

_generator: Callable | None = None


def _answer_clean(value: str) -> str:
    return " ".join(value.strip().split())


def _split_candidates(output: str) -> list[str]:
    """Separa la salida del modelo en candidatos de distractor."""
    parts = re.split(r"[;|\n]+", output)
    cleaned: list[str] = []
    for part in parts:
        text = re.sub(r"^\s*\d+[.)]\s*", "", part.strip())
        candidate = _answer_clean(text)
        if candidate:
            cleaned.append(candidate)
    return cleaned


def generate_distractors(
    question: str,
    answer: str,
    count: int = DISTRACTOR_COUNT,
) -> list[str]:
    """Genera distractores plausibles en lenguaje natural viendo la pregunta."""
    try:
        generator = _get_generator()
        prompt = (
            f"Pregunta: {question}\n"
            f"Respuesta correcta: {answer}\n"
            f"Genera {count} respuestas incorrectas pero creibles para esa pregunta, "
            "en espanol, separadas con punto y coma."
        )
        output = generator(
            prompt,
            max_new_tokens=48,
            do_sample=True,
            temperature=0.9,
        )[0]["generated_text"]
        candidates = _split_candidates(output or "")
    except Exception:
        candidates = []

    clean_correct = _answer_clean(answer).lower()
    distractors: list[str] = []
    for candidate in candidates:
        if candidate.lower() == clean_correct or candidate in distractors:
            continue
        distractors.append(candidate)
        if len(distractors) >= count:
            break

    fallbacks = ("Ninguna de las anteriores", "Todas las anteriores", "No se puede saber")
    for fallback in fallbacks:
        if len(distractors) >= count:
            break
        if fallback.lower() == clean_correct or fallback in distractors:
            continue
        distractors.append(fallback)

    return distractors[:count]


def build_options(question: str, answer: str) -> list[str]:
    """Devuelve 4 opciones: la respuesta correcta y 3 distractores generados."""
    correct = _answer_clean(answer)
    if not correct:
        raise ValueError("La respuesta no puede estar vacía")

    distractors = generate_distractors(question, correct, DISTRACTOR_COUNT)
    options = [correct, *distractors]
    shuffle(options)
    return options


def _get_generator() -> Callable:
    """Carga una vez el pipeline local de generacion de texto."""
    global _generator
    if _generator is None:
        from transformers import pipeline

        _generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-small",
        )
    return _generator