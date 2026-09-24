import pytest

from app.options import build_options, generate_distractors


def patch_generator(monkeypatch, text: str | None = None, raiser: type[Exception] | None = None):
    def _fake():
        class _FakeGenerator:
            def __call__(self, prompt, **kwargs):
                if raiser is not None:
                    raise raiser("model unavailable")
                return [{"generated_text": text or "Cordoba; Rosario; Mendoza"}]
        return _FakeGenerator()
    monkeypatch.setattr("app.options._get_generator", _fake)


def test_build_options_returns_four_options_including_the_answer(monkeypatch):
    patch_generator(monkeypatch)

    options = build_options("¿Cuál es la capital de Argentina?", "Buenos Aires")

    assert len(options) == 4
    assert len(set(options)) == 4
    assert "Buenos Aires" in options
    assert {"Cordoba", "Rosario", "Mendoza"}.issubset(set(options))


def test_generate_distractors_discards_the_correct_answer(monkeypatch):
    patch_generator(monkeypatch, "Buenos Aires; Cordoba; Mendoza; Rosario")

    distractors = generate_distractors(
        "¿Cuál es la capital de Argentina?", "Buenos Aires"
    )

    assert "Buenos Aires" not in distractors
    assert distractors == ["Cordoba", "Mendoza", "Rosario"]


def test_generate_distractors_strips_numbering_and_whitespace(monkeypatch):
    patch_generator(monkeypatch, "1. Cordoba\n2. Rosario\n3.  Mendoza ")

    distractors = generate_distractors("¿Cuál es la capital?", "Buenos Aires")

    assert distractors == ["Cordoba", "Rosario", "Mendoza"]


def test_generate_distractors_pads_with_fallbacks_when_output_is_empty(monkeypatch):
    patch_generator(monkeypatch, "   \n ")

    distractors = generate_distractors("¿Cuál es la capital?", "Buenos Aires")

    assert len(distractors) == 3
    assert "Buenos Aires" not in distractors


def test_generate_distractors_falls_back_when_the_model_fails(monkeypatch):
    patch_generator(monkeypatch, raiser=RuntimeError)

    distractors = generate_distractors("¿Cuál es la capital?", "Buenos Aires")

    assert len(distractors) == 3
    assert "Buenos Aires" not in distractors


def test_build_options_rejects_an_empty_answer(monkeypatch):
    patch_generator(monkeypatch)

    with pytest.raises(ValueError):
        build_options("¿Una pregunta?", "   ")