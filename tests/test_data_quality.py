from app.load_data import (
    CAREQA_DATASET,
    DEFAULT_DATASET,
    _metadata_as_dict,
    careqa_row_to_fields,
    simpleqa_row_to_fields,
)
from app.models import CAREQA_ES_DATASET


def _careqa_row(**overrides):
    row = {
        "question": "  ¿Cuál es el tratamiento?  ",
        "op1": " Primera opción ",
        "op2": "Segunda opción",
        "op3": "Tercera opción",
        "op4": "Cuarta opción",
        "cop": 2,
        "category": "Medicine",
    }
    row.update(overrides)
    return row


def test_careqa_row_to_fields_preserves_options_and_correct_answer():
    result = careqa_row_to_fields(_careqa_row())

    assert result == {
        "question": "¿Cuál es el tratamiento?",
        "answer": "Segunda opción",
        "category": "Medicine",
        "source": CAREQA_ES_DATASET,
        "dataset_choices": [
            "Primera opción",
            "Segunda opción",
            "Tercera opción",
            "Cuarta opción",
        ],
    }
    assert DEFAULT_DATASET == CAREQA_DATASET


def test_careqa_row_to_fields_rejects_invalid_rows():
    assert careqa_row_to_fields(_careqa_row(question="  ")) is None
    assert careqa_row_to_fields(_careqa_row(op3="")) is None
    assert careqa_row_to_fields(_careqa_row(op4="Segunda opción")) is None
    assert careqa_row_to_fields(_careqa_row(cop=0)) is None
    assert careqa_row_to_fields(_careqa_row(cop=5)) is None
    assert careqa_row_to_fields(_careqa_row(cop="invalid")) is None


def test_metadata_as_dict_reads_json_text():
    metadata = '{"topic": "science"}'

    assert _metadata_as_dict(metadata) == {"topic": "science"}


def test_metadata_as_dict_returns_empty_dict_for_invalid_text():
    assert _metadata_as_dict("this is not metadata") == {}


def test_simpleqa_row_to_fields_cleans_a_valid_row():
    row = {
        "problem": "  What is gravity?  ",
        "answer": "  A force  ",
        "metadata": {"topic": "science", "urls": [" https://example.com/source "]},
    }

    assert simpleqa_row_to_fields(row) == {
        "question": "What is gravity?",
        "answer": "A force",
        "category": "science",
        "source": "https://example.com/source",
    }


def test_simpleqa_row_to_fields_returns_none_when_answer_is_missing():
    row = {"problem": "What is gravity?", "answer": None}

    assert simpleqa_row_to_fields(row) is None


def test_simpleqa_row_to_fields_limits_long_category_and_source():
    row = {
        "problem": "A question",
        "answer": "An answer",
        "metadata": {
            "topic": "t" * 120,
            "urls": ["u" * 300],
        },
    }

    result = simpleqa_row_to_fields(row)

    assert len(result["category"]) == 100
    assert len(result["source"]) == 255
