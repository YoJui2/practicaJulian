from app.load_data import _metadata_as_dict, simpleqa_row_to_fields
from app.data_quality import MAX_QUESTION_LENGTH


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


def test_simpleqa_row_rejects_questions_over_the_character_limit():
    row = {
        "problem": "q" * (MAX_QUESTION_LENGTH + 1),
        "answer": "An answer",
    }

    assert simpleqa_row_to_fields(row) is None


def test_simpleqa_row_accepts_question_at_the_character_limit():
    row = {
        "problem": "q" * MAX_QUESTION_LENGTH,
        "answer": "An answer",
    }

    assert len(simpleqa_row_to_fields(row)["question"]) == MAX_QUESTION_LENGTH
