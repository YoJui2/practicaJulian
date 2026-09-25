from unittest.mock import MagicMock

import pytest

from app.models import Question, Translation
from app.translate import (
    get_untranslated_questions,
    save_translation,
    translate_all,
    translate_100,
    translate_250,
    translate_500,
)


def test_save_translation_adds_and_commits():
    db = MagicMock()

    save_translation(db, 3, "es", "¿Cuál es la capital?", "Buenos Aires")

    saved = db.add.call_args.args[0]
    assert isinstance(saved, Translation)
    assert saved.question_id == 3
    assert saved.lang == "es"
    assert saved.question_translated == "¿Cuál es la capital?"
    assert saved.answer_translated == "Buenos Aires"
    assert saved.is_automatic is True
    db.commit.assert_called_once_with()
    db.rollback.assert_not_called()


def test_save_translation_rolls_back_and_raises_runtime_error():
    db = MagicMock()
    db.commit.side_effect = ValueError("database unavailable")

    with pytest.raises(RuntimeError, match="No se pudo guardar la traducción"):
        save_translation(db, 3, "es", "¿Qué?", "Resp")

    db.add.assert_called_once()
    db.rollback.assert_called_once_with()


def test_get_untranslated_questions_excludes_translated_ones():
    db = MagicMock()
    result = object()
    db.query(Question).filter.return_value.all.return_value = result

    questions = get_untranslated_questions(db, "es")

    queried_entities = [call.args[0] for call in db.query.call_args_list]
    assert any(entity is Translation.question_id for entity in queried_entities)
    assert any(entity is Question for entity in queried_entities)
    assert db.query(Question).filter.call_count == 2
    assert questions is result


def test_fixed_size_translation_functions_process_the_requested_limit(monkeypatch):
    limits = []

    def fake_translate_all(**kwargs):
        limits.append(kwargs["max_questions"])

    monkeypatch.setattr("app.translate.translate_all", fake_translate_all)

    translate_100()
    translate_250()
    translate_500()

    assert limits == [100, 250, 500]


def test_translate_all_processes_pending_questions(monkeypatch):
    class _FakeQuestion:
        def __init__(self, id, question, answer):
            self.id = id
            self.question = question
            self.answer = answer

    pending = [
        _FakeQuestion(1, "Where is Argentina?", "South America"),
        _FakeQuestion(2, "What is the capital of Spain?", "Madrid"),
    ]
    saved = []

    monkeypatch.setattr(
        "app.translate.get_untranslated_questions",
        lambda db, lang: pending,
    )
    monkeypatch.setattr(
        "app.translate.translate_text",
        lambda text: f"[{text}]",
    )

    def fake_save_translation(
        db,
        question_id,
        lang,
        question_translated,
        answer_translated,
        is_automatic=True,
    ):
        saved.append(
            (question_id, lang, question_translated, answer_translated, is_automatic)
        )

    monkeypatch.setattr("app.translate.save_translation", fake_save_translation)

    translate_all(max_questions=100)

    assert saved == [
        (1, "es", "[Where is Argentina?]", "[South America]", True),
        (2, "es", "[What is the capital of Spain?]", "[Madrid]", True),
    ]


def test_translate_all_skips_questions_without_text(monkeypatch):
    class _FakeQuestion:
        def __init__(self, id, question, answer):
            self.id = id
            self.question = question
            self.answer = answer

    pending = [_FakeQuestion(1, "", "answer"), _FakeQuestion(2, "q", "")]
    saved = []

    monkeypatch.setattr(
        "app.translate.get_untranslated_questions",
        lambda db, lang: pending,
    )
    monkeypatch.setattr(
        "app.translate.translate_text",
        lambda text: f"[{text}]",
    )
    monkeypatch.setattr(
        "app.translate.save_translation",
        lambda db, question_id, lang, question_translated, answer_translated, is_automatic=True: saved.append(
            question_id
        ),
    )

    translate_all(max_questions=100)

    assert saved == []