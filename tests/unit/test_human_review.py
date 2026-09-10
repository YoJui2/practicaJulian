from app.human_review import ask_human_for_category, confirm_ai_suggestion


CATEGORIES = [
    {"name": "history", "label": "Historia"},
    {"name": "music", "label": "Música"},
]


def test_ask_human_for_category_returns_selected_name(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "2")

    assert ask_human_for_category(CATEGORIES) == "music"


def test_ask_human_for_category_retries_invalid_choice(monkeypatch):
    choices = iter(["0", "1"])
    monkeypatch.setattr("builtins.input", lambda _: next(choices))

    assert ask_human_for_category(CATEGORIES) == "history"


def test_ask_human_for_category_returns_none_for_skip(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "s")

    assert ask_human_for_category(CATEGORIES) is None


def test_confirm_ai_suggestion_accepts_yes(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "s")

    assert confirm_ai_suggestion("history", 0.8) is True


def test_confirm_ai_suggestion_accepts_empty_answer(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")

    assert confirm_ai_suggestion("history", 0.8) is True


def test_confirm_ai_suggestion_rejects_no(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "n")

    assert confirm_ai_suggestion("history", 0.8) is False


def test_confirm_ai_suggestion_defaults_to_accept_unknown_answer(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "maybe")

    assert confirm_ai_suggestion("history", 0.8) is True
