from unittest.mock import MagicMock

import pytest

from app.categorize import categorize_100, categorize_250, categorize_500, save_categorization
from app.models import Categorization


def test_save_categorization_adds_and_commits():
    db = MagicMock()

    save_categorization(db, 7, "history", 0.85, is_automatic=True)

    saved = db.add.call_args.args[0]
    assert isinstance(saved, Categorization)
    assert saved.question_id == 7
    assert saved.category_name == "history"
    assert saved.confidence_score == 0.85
    assert saved.is_automatic is True
    db.commit.assert_called_once_with()
    db.rollback.assert_not_called()


def test_save_categorization_rolls_back_and_raises_runtime_error():
    db = MagicMock()
    db.commit.side_effect = ValueError("database unavailable")

    with pytest.raises(RuntimeError, match="No se pudo guardar la categorización"):
        save_categorization(db, 7, "history", 0.85, is_automatic=False)

    db.add.assert_called_once()
    db.rollback.assert_called_once_with()


def test_fixed_size_categorization_functions_process_the_requested_limit(monkeypatch):
    limits = []

    def fake_categorize_all(**kwargs):
        limits.append(kwargs["max_questions"])

    monkeypatch.setattr("app.categorize.categorize_all", fake_categorize_all)

    categorize_100()
    categorize_250()
    categorize_500()

    assert limits == [100, 250, 500]


