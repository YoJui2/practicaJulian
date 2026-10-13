import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.data_quality import MAX_QUESTION_LENGTH
from app.load_data import (
    build_argument_parser,
    load_opentrivia_questions,
    opentrivia_row_to_fields,
)
from app.models import Question


def test_opentrivia_row_maps_category_and_preserves_choices():
    row = {
        "category": "sports",
        "question": " Which team won? ",
        "choices": [" Team A ", "Team B", "Team C", "Team D"],
        "answer": "Team B",
    }

    assert opentrivia_row_to_fields(row) == {
        "question": "Which team won?",
        "answer": "Team B",
        "options": ["Team A", "Team B", "Team C", "Team D"],
        "category": "deportes",
        "source": "OpenTriviaQA: sports",
    }


def test_opentrivia_row_keeps_ambiguous_source_categories_unmapped():
    row = {
        "category": "world",
        "question": "Who was the first person to orbit Earth?",
        "choices": ["A", "B", "C", "D"],
        "answer": "A",
    }

    result = opentrivia_row_to_fields(row)

    assert result["category"] is None
    assert result["source"] == "OpenTriviaQA: world"


def test_opentrivia_row_uses_the_matching_choice_as_the_answer():
    row = {
        "category": "literature",
        "question": "Who wrote Hamlet?",
        "choices": [
            "Charles Dickens",
            "William Shakespeare",
            "Jane Austen",
            "Mark Twain",
        ],
        "answer": "  william   shakespeare ",
    }

    result = opentrivia_row_to_fields(row)

    assert result["answer"] == "William Shakespeare"
    assert result["category"] == "arte"


def test_opentrivia_row_preserves_two_choices_and_removes_duplicates():
    row = {
        "category": "animals",
        "question": "Are cats mammals?",
        "choices": ["True", "False", "False"],
        "answer": "True",
    }

    result = opentrivia_row_to_fields(row)

    assert result["options"] == ["True", "False"]
    assert result["answer"] == "True"


def test_opentrivia_row_rejects_missing_or_invalid_choices():
    row = {
        "category": "history",
        "question": "When?",
        "choices": ["A"],
        "answer": "A",
    }

    assert opentrivia_row_to_fields(row) is None


def test_opentrivia_row_rejects_questions_over_the_character_limit():
    row = {
        "category": "history",
        "question": "q" * (MAX_QUESTION_LENGTH + 1),
        "choices": ["A", "B"],
        "answer": "A",
    }

    assert opentrivia_row_to_fields(row) is None


def test_opentrivia_row_accepts_question_at_the_character_limit():
    row = {
        "category": "history",
        "question": "q" * MAX_QUESTION_LENGTH,
        "choices": ["A", "B"],
        "answer": "A",
    }

    result = opentrivia_row_to_fields(row)

    assert len(result["question"]) == MAX_QUESTION_LENGTH


def test_loader_defaults_to_opentrivia_and_keeps_simpleqa_selectable():
    parser = build_argument_parser()

    assert parser.parse_args([]).dataset == "opentriviaqa"
    assert parser.parse_args(["--dataset", "simpleqa"]).dataset == "simpleqa"


def test_load_opentrivia_persists_options_and_direct_category(monkeypatch):
    engine = create_engine("sqlite://")
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine)
    monkeypatch.setattr("app.load_data.engine", engine)
    monkeypatch.setattr("app.load_data.SessionLocal", test_session)
    monkeypatch.setattr(
        "app.load_data._download_opentrivia_frames",
        lambda: pd.DataFrame(
            [
                {
                    "category": "sports",
                    "question": "Who won?",
                    "choices": ["Team A", "Team B"],
                    "answer": "Team A",
                },
                {
                    "category": "world",
                    "question": "Where is it?",
                    "choices": ["Here", "There"],
                    "answer": "Here",
                },
            ]
        ),
    )

    try:
        load_opentrivia_questions()
        with test_session() as db:
            questions = db.query(Question).order_by(Question.id).all()

            assert [option.text for option in questions[0].options] == [
                "Team A",
                "Team B",
            ]
            assert questions[0].category == "deportes"
            assert [item.category_name for item in questions[0].categorizations] == [
                "deportes"
            ]
            assert questions[1].category is None
            assert questions[1].categorizations == []
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
