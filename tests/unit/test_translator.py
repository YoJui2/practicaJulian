import pytest

from app.translator import (
    looks_spanish,
    needs_translation,
    translate_text,
    translate_texts,
)


def test_translate_text_decodes_model_output(monkeypatch):
    tokenized_inputs = {"input_ids": [[1, 2, 3]]}

    class _FakeTokenizer:
        def __call__(self, texts, **kwargs):
            assert texts == ["What is the capital of France?"]
            assert kwargs["padding"] is True
            return tokenized_inputs

        def decode(self, sequence, **kwargs):
            return "¿Cuál es la capital de Francia?"

    class _FakeModel:
        def generate(self, **kwargs):
            assert kwargs["input_ids"] == tokenized_inputs["input_ids"]
            return [[1, 4, 5]]

    monkeypatch.setattr("app.translator._get_translator", lambda: (_FakeTokenizer(), _FakeModel()))

    translated = translate_text("What is the capital of France?")

    assert translated == "¿Cuál es la capital de Francia?"


def test_translate_text_strips_whitespace(monkeypatch):
    class _FakeTokenizer:
        def __call__(self, texts, **kwargs):
            return {"input_ids": [[1, 2]]}

        def decode(self, sequence, **kwargs):
            return "  Buenos Aires  "

    class _FakeModel:
        def generate(self, **kwargs):
            return [[1]]

    monkeypatch.setattr("app.translator._get_translator", lambda: (_FakeTokenizer(), _FakeModel()))

    assert translate_text("Buenos Aires") == "Buenos Aires"


class _BatchTokenizer:
    def __init__(self):
        self.texts = []

    def __call__(self, texts, **kwargs):
        self.texts = list(texts)
        return {"input_ids": [[1] for _ in texts]}

    def decode(self, sequence, **kwargs):
        return f"es:{self.texts[sequence[0]]}"


class _BatchModel:
    def generate(self, **kwargs):
        return [[index] for index in range(len(kwargs["input_ids"]))]


def test_translate_texts_translates_every_text_in_a_single_batch(monkeypatch):
    tokenizer = _BatchTokenizer()
    monkeypatch.setattr(
        "app.translator._get_translator",
        lambda: (tokenizer, _BatchModel()),
    )

    translated = translate_texts(["Who wrote Hamlet?", "William Shakespeare"])

    assert translated == ["es:Who wrote Hamlet?", "es:William Shakespeare"]


def test_translate_texts_reuses_previous_translations(monkeypatch):
    calls = []

    class _CountingModel:
        def generate(self, **kwargs):
            calls.append(kwargs["input_ids"])
            return [[index] for index in range(len(kwargs["input_ids"]))]

    monkeypatch.setattr(
        "app.translator._get_translator",
        lambda: (_BatchTokenizer(), _CountingModel()),
    )

    first = translate_texts(["Who wrote Hamlet?"])
    second = translate_texts(["Who wrote Hamlet?"])

    assert first == second == ["es:Who wrote Hamlet?"]
    assert len(calls) == 1


def test_translate_texts_keeps_texts_already_in_spanish(monkeypatch):
    monkeypatch.setattr(
        "app.translator._get_translator",
        lambda: (_BatchTokenizer(), _BatchModel()),
    )

    translated = translate_texts(["¿Cuál es la capital de Argentina?"])

    assert translated == ["¿Cuál es la capital de Argentina?"]


def test_translate_texts_translates_each_repeated_text_only_once(monkeypatch):
    monkeypatch.setattr(
        "app.translator._get_translator",
        lambda: (_BatchTokenizer(), _BatchModel()),
    )

    translated = translate_texts(["Rosario", "Rosario", "Mendoza"])

    assert translated == ["es:Rosario", "es:Rosario", "es:Mendoza"]


@pytest.mark.parametrize(
    "text",
    [
        "¿Cuál es la capital de Argentina?",
        "Ninguna de las anteriores",
        "El lugar de la pregunta",
    ],
)
def test_looks_spanish_detects_spanish_text(text):
    assert looks_spanish(text) is True


@pytest.mark.parametrize(
    "text",
    [
        "Who wrote Hamlet?",
        "William Shakespeare",
        "Rosario",
    ],
)
def test_looks_spanish_detects_non_spanish_text(text):
    assert looks_spanish(text) is False


@pytest.mark.parametrize(
    "text",
    ["", "   ", "1985", "¿Cuál es la capital?"],
)
def test_needs_translation_skips_text_that_should_not_be_translated(text):
    assert needs_translation(text) is False


def test_needs_translation_accepts_english_text():
    assert needs_translation("Who wrote Hamlet?") is True