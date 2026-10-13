"""Traducción de preguntas y respuestas con IA.

Usa un modelo secuencia a secuencia (Helsinki-NLP/opus-mt-en-es por defecto)
para traducir texto al español. El modelo se carga una vez y queda cacheado.

Los textos que ya están en español (o que son solo números) se devuelven sin
traducir, y cada traducción se memoriza para no volver a pagar el mismo cálculo.
"""

import re
from os import environ

DEFAULT_TARGET_LANG = "es"
DEFAULT_SOURCE_LANG = "en"
DEFAULT_TRANSLATION_MODEL = "Helsinki-NLP/opus-mt-en-es"
MAX_INPUT_TOKENS = 512
MAX_GENERATED_TOKENS = 512

SPANISH_MARKERS = frozenset(
    {
        "al",
        "como",
        "con",
        "cual",
        "cuál",
        "cuando",
        "cuanto",
        "cuánto",
        "cuándo",
        "de",
        "del",
        "donde",
        "dónde",
        "el",
        "en",
        "es",
        "esta",
        "está",
        "estan",
        "están",
        "la",
        "las",
        "lo",
        "los",
        "mas",
        "más",
        "o",
        "para",
        "pero",
        "por",
        "que",
        "qué",
        "quien",
        "quién",
        "se",
        "son",
        "su",
        "sus",
        "un",
        "una",
        "y",
    }
)

_WORD_PATTERN = re.compile(r"[^\W\d_]+", re.UNICODE)
_ONLY_NUMBERS_PATTERN = re.compile(r"^[\W\d_]+$", re.UNICODE)

_translator: tuple | None = None
_cache: dict[str, str] = {}


def _get_translator() -> tuple:
    """Carga una vez el modelo local de traducción y su tokenizador."""
    global _translator
    if _translator is None:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        model_name = environ.get("TRANSLATION_MODEL", DEFAULT_TRANSLATION_MODEL)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        _translator = (tokenizer, model)
    return _translator


def looks_spanish(text: str) -> bool:
    """Indica si un texto ya está escrito en español."""
    stripped = text.strip()
    if not stripped:
        return False
    if stripped.startswith(("¿", "¡")):
        return True
    words = {word.lower() for word in _WORD_PATTERN.findall(stripped)}
    return bool(words & SPANISH_MARKERS)


def needs_translation(text: str) -> bool:
    """Indica si un texto tiene sentido pasar por el modelo de traducción."""
    if not text or not text.strip():
        return False
    if _ONLY_NUMBERS_PATTERN.match(text):
        return False
    return not looks_spanish(text)


def _generate(texts: list[str]) -> list[str]:
    tokenizer, model = _get_translator()
    inputs = tokenizer(
        texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=MAX_INPUT_TOKENS,
    )
    outputs = model.generate(**inputs, max_length=MAX_GENERATED_TOKENS)
    return [
        tokenizer.decode(sequence, skip_special_tokens=True).strip()
        for sequence in outputs
    ]


def translate_texts(texts: list[str]) -> list[str]:
    """Traduce varios textos en una sola pasada, reutilizando traducciones ya hechas."""
    unique = dict.fromkeys(texts)
    pending = [
        text
        for text in unique
        if needs_translation(text) and text not in _cache
    ]
    if pending:
        for text, translation in zip(pending, _generate(pending)):
            _cache[text] = translation

    return [
        _cache[text] if needs_translation(text) and text in _cache else text
        for text in texts
    ]


def translate_text(text: str) -> str:
    """Traduce un texto al español usando el modelo cargado."""
    return translate_texts([text])[0]
