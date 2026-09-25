import pytest

from app.live_translation import (
    _match_translated_answer as match_translated_answer,
)
from app.live_translation import build_english_options, translate_question


@pytest.fixture(autouse=True)
def fake_options(monkeypatch):
    monkeypatch.setattr(
        "app.live_translation.build_options",
        lambda question, answer: [answer, "Cordoba", "Rosario", "Mendoza"],
    )


@pytest.fixture(autouse=True)
def fake_translation(monkeypatch):
    def fake_translate_texts(texts):
        return [f"es:{text}" for text in texts]

    monkeypatch.setattr(
        "app.live_translation.translate_texts",
        fake_translate_texts,
    )


def test_build_english_options_generates_options_in_the_source_language():
    options = build_english_options("Who wrote Hamlet?", "William Shakespeare")

    assert len(options) == 4
    assert "William Shakespeare" in options


def test_translate_question_translates_the_question_and_every_option():
    result = translate_question("Who wrote Hamlet?", "William Shakespeare")

    assert result["question"] == "es:Who wrote Hamlet?"
    assert result["options"] == [
        "es:William Shakespeare",
        "es:Cordoba",
        "es:Rosario",
        "es:Mendoza",
    ]
    assert result["lang"] == "es"


def test_translate_question_keeps_the_answer_inside_the_translated_options():
    result = translate_question("Who wrote Hamlet?", "William Shakespeare")

    assert result["answer"] in result["options"]
    assert result["answer"] == "es:William Shakespeare"


def test_translate_question_returns_the_source_text_as_original():
    result = translate_question("Who wrote Hamlet?", "William Shakespeare")

    assert result["original"] == {
        "question": "Who wrote Hamlet?",
        "answer": "William Shakespeare",
        "options": ["William Shakespeare", "Cordoba", "Rosario", "Mendoza"],
        "lang": "en",
    }


def test_translate_question_accepts_prebuilt_options():
    result = translate_question(
        "Who wrote Hamlet?",
        "William Shakespeare",
        options=["William Shakespeare", "Cordoba", "Rosario", "Mendoza"],
    )

    assert result["options"] == [
        "es:William Shakespeare",
        "es:Cordoba",
        "es:Rosario",
        "es:Mendoza",
    ]


def test_translate_question_honours_the_requested_language():
    result = translate_question(
        "Who wrote Hamlet?",
        "William Shakespeare",
        target_lang="pt",
    )

    assert result["lang"] == "pt"


def test_match_translated_answer_comparates_without_extra_spaces():
    translated = match_translated_answer(
        "  William   Shakespeare  ",
        ["William Shakespeare", "Cordoba"],
        ["es:William Shakespeare", "es:Cordoba"],
    )

    assert translated == "es:William Shakespeare"


def test_match_translated_answer_translates_when_the_answer_is_not_an_option():
    translated = match_translated_answer(
        "William Shakespeare",
        ["Cordoba", "Rosario"],
        ["es:Cordoba", "es:Rosario"],
    )

    assert translated == "es:William Shakespeare"
