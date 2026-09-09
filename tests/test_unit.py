from app.load_data import simpleqa_row_to_fields


def test_simpleqa_row_to_fields_maps_and_normalizes_a_valid_row():
    row = {
        "problem": "  What is a vector database? ",
        "answer": " A database for embeddings. ",
        "metadata": {"topic": "AI", "urls": ["https://example.com"]},
    }

    assert simpleqa_row_to_fields(row) == {
        "question": "What is a vector database?",
        "answer": "A database for embeddings.",
        "category": "AI",
        "source": "https://example.com",
    }


def test_simpleqa_row_to_fields_discards_rows_without_question_or_answer():
    assert simpleqa_row_to_fields({"problem": "", "answer": "42"}) is None
    assert simpleqa_row_to_fields({"problem": "What?", "answer": None}) is None