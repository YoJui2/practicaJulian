"""Generacion de opciones de opcion multiple a partir de la pregunta."""

import re
from os import environ
from random import shuffle
from typing import Callable

DISTRACTOR_COUNT = 3
GENERIC_OPTIONS = {
    "all of the above",
    "none of the above",
    "ninguna de las anteriores",
    "todas las anteriores",
    "no se puede saber",
}

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
            "Create plausible incorrect answers for this multiple-choice question. "
            "Use the same language as the question. Do not use generic options such "
            "as 'none of the above' or 'all of the above'. Return only the answers, "
            "one per line, with no numbering or explanation.\n"
            f"Question: {question}\n"
            f"Correct answer: {answer}\n"
            f"Number of incorrect answers: {count}\n"
            "If the correct answer is a number, return different plausible numbers "
            "near it, not words or team names."
        )
        outputs = generator(
            prompt,
            max_new_tokens=48,
            do_sample=True,
            temperature=0.9,
            num_return_sequences=count * 2,
        )
        candidates = []
        for result in outputs:
            candidates.extend(_split_candidates(result.get("generated_text", "")))
    except Exception:
        candidates = []

    clean_correct = _answer_clean(answer).lower()
    distractors: list[str] = []
    for candidate in candidates:
        if (
            candidate.lower() == clean_correct
            or candidate.lower() in GENERIC_OPTIONS
            or candidate.lower() in {item.lower() for item in distractors}
        ):
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
    """Carga una vez el modelo local de generacion secuencia a secuencia."""
    global _generator
    if _generator is None:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        model_name = environ.get("OPTIONS_MODEL", "google/flan-t5-base")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        def generate(prompt: str, **kwargs: object) -> list[dict[str, str]]:
            inputs = tokenizer(prompt, return_tensors="pt")
            output = model.generate(**inputs, **kwargs)
            return [
                {
                    "generated_text": tokenizer.decode(
                        sequence,
                        skip_special_tokens=True,
                    )
                }
                for sequence in output
            ]

        _generator = generate
    return _generator