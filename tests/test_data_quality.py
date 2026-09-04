import pandas as pd

from app.load_data import _metadata_as_dict, simpleqa_row_to_fields


def test_metadata_as_dict_accepts_json_and_python_literal():
    assert _metadata_as_dict('{"topic": "science", "urls": ["https://example.com"]}') == {
        "topic": "science",
        "urls": ["https://example.com"],
    }
    assert _metadata_as_dict("{'topic': 'history'}") == {"topic": "history"}


def test_metadata_as_dict_returns_empty_dict_for_invalid_values():
    for value in (None, float("nan"), "", "not metadata", ["not", "a", "dict"]):
        assert _metadata_as_dict(value) == {}


def test_simpleqa_row_to_fields_maps_and_cleans_valid_row():
    row = pd.Series(
        {
            "problem": "  What is gravity?  ",
            "answer": "  A force  ",
            "metadata": {
                "topic": "science",
                "urls": [" https://example.com/source ", "https://other.example"],
            },
        }
    )

    assert simpleqa_row_to_fields(row) == {
        "question": "What is gravity?",
        "answer": "A force",
        "category": "science",
        "source": "https://example.com/source",
    }


def test_simpleqa_row_to_fields_supports_question_alias_and_metadata_text():
    row = {
        "question": "Who wrote Hamlet?",
        "answer": "William Shakespeare",
        "metadata": "{'topic': 'history', 'urls': ['https://example.com']} ",
    }

    result = simpleqa_row_to_fields(row)

    assert result["question"] == "Who wrote Hamlet?"
    assert result["answer"] == "William Shakespeare"
    assert result["category"] == "history"
    assert result["source"] == "https://example.com"


def test_simpleqa_row_to_fields_discards_incomplete_rows():
    for row in (
        {"problem": None, "answer": "answer"},
        {"problem": "question", "answer": None},
        {"problem": "   ", "answer": "answer"},
        {"problem": "question", "answer": "   "},
    ):
        assert simpleqa_row_to_fields(row) is None


def test_simpleqa_row_to_fields_applies_database_field_limits():
    row = {
        "problem": "question",
        "answer": "answer",
        "metadata": {
            "topic": "t" * 120,
            "urls": ["u" * 300],
        },
    }

    result = simpleqa_row_to_fields(row)

    assert len(result["category"]) == 100
    assert len(result["source"]) == 255
