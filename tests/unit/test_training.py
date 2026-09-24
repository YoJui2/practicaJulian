from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Categorization, Question
from app.training import TrainingExample, load_manual_examples, split_training_data, train_model


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_load_manual_examples_uses_latest_manual_label(db_session):
    question = Question(question="  What is gravity?  ", answer="A force")
    db_session.add(question)
    db_session.flush()
    db_session.add_all(
        [
            Categorization(
                question_id=question.id,
                category_name="science",
                is_automatic=False,
                created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            ),
            Categorization(
                question_id=question.id,
                category_name="history",
                is_automatic=False,
                created_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
            ),
            Categorization(
                question_id=question.id,
                category_name="geography",
                is_automatic=True,
            ),
        ]
    )
    db_session.commit()

    assert load_manual_examples(db_session) == [
        TrainingExample("What is gravity?", "history", question.id)
    ]


def test_load_manual_examples_excludes_automatic_and_blank_questions(db_session):
    blank = Question(question="   ", answer="answer")
    automatic = Question(question="Who wrote Hamlet?", answer="Shakespeare")
    db_session.add_all([blank, automatic])
    db_session.flush()
    db_session.add_all(
        [
            Categorization(question_id=blank.id, category_name="science", is_automatic=False),
            Categorization(question_id=automatic.id, category_name="art", is_automatic=True),
        ]
    )
    db_session.commit()

    assert load_manual_examples(db_session) == []


def test_split_training_data_is_reproducible_and_stratified():
    examples = [
        TrainingExample(f"science {index}", "science", index)
        for index in range(5)
    ] + [
        TrainingExample(f"history {index}", "history", index + 5)
        for index in range(5)
    ]

    train, validation = split_training_data(examples, validation_size=0.2)

    repeated_train, _ = split_training_data(examples, validation_size=0.2)

    assert train == repeated_train
    assert {example.label for example in validation} == {"science", "history"}


def test_train_model_persists_supervised_artifact(db_session, tmp_path):
    for index in range(6):
        question = Question(
            question=f"science gravity physics {index}",
            answer="answer",
        )
        db_session.add(question)
        db_session.flush()
        db_session.add(
            Categorization(
                question_id=question.id,
                category_name="science",
                is_automatic=False,
            )
        )

    for index in range(6):
        question = Question(
            question=f"history empire war {index}",
            answer="answer",
        )
        db_session.add(question)
        db_session.flush()
        db_session.add(
            Categorization(
                question_id=question.id,
                category_name="history",
                is_automatic=False,
            )
        )
    db_session.commit()

    report = train_model(db_session, tmp_path / "modelomainv1.pkl")

    assert report.model_path.exists()
    assert report.training_examples == 9
    assert report.validation_examples == 3
    assert report.metrics["accuracy"] == 1.0