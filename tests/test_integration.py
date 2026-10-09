import pytest
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import app
from app.models import Categorization, Question, QuestionOption


def test_api_can_create_read_and_count_a_question(client):
    response = client.post(
        "/questions",
        json={
            "question": "Who wrote Hamlet?",
            "answer": "William Shakespeare",
            "category": "history",
            "source": "book",
        },
    )

    assert response.status_code == 201
    question = response.json()
    question_id = question["id"]
    assert question["question"] == "Who wrote Hamlet?"

    listed = client.get("/questions?skip=0&limit=10")
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [question_id]

    retrieved = client.get(
        f"/questions/{question_id}",
        headers={"Origin": "http://localhost:5173"},
    )
    assert retrieved.status_code == 200
    body = retrieved.json()
    assert body["question"] == "es:Who wrote Hamlet?"
    assert body["answer"] == "es:William Shakespeare"
    assert body["lang"] == "es"
    assert len(body["options"]) == 4
    assert len(set(body["options"])) == 4
    assert "es:William Shakespeare" in body["options"]
    assert {"es:Cordoba", "es:Rosario", "es:Mendoza"}.issubset(
        set(body["options"])
    )
    assert retrieved.headers["access-control-allow-origin"] == (
        "http://localhost:5173"
    )

    stats = client.get("/stats")
    assert stats.json() == {"total": 1, "by_category": {"history": 1}}


def test_get_question_options_are_generated_instead_of_read_from_the_dataset(client):
    created = client.post(
        "/questions",
        json={
            "question": "Pregunta unica?",
            "answer": "Respuesta Unica",
            "category": "solo",
        },
    )
    assert created.status_code == 201

    body = client.get(f"/questions/{created.json()['id']}").json()

    assert len(body["options"]) == 4
    assert len(set(body["options"])) == 4
    assert body["answer"] == "es:Respuesta Unica"
    assert "es:Respuesta Unica" in body["options"]
    assert {"es:Cordoba", "es:Rosario", "es:Mendoza"}.issubset(
        set(body["options"])
    )


def test_get_question_translates_the_dataset_options(client, monkeypatch):
    created = client.post(
        "/questions",
        json={
            "question": "Which planet is known as the Red Planet?",
            "answer": "Mars",
        },
    )
    question_id = created.json()["id"]
    db_generator = app.dependency_overrides[get_db]()
    db: Session = next(db_generator)
    try:
        question = db.query(Question).filter(Question.id == question_id).one()
        question.options = [
            QuestionOption(position=index, text=option)
            for index, option in enumerate(
                ["Mars", "Venus", "Jupiter", "Saturn"]
            )
        ]
        db.commit()
    finally:
        db.close()
        db_generator.close()

    monkeypatch.setattr(
        "app.main.build_options",
        lambda *_: pytest.fail("dataset options should be reused"),
    )

    english = client.get(f"/questions/{question_id}?lang=en").json()
    spanish = client.get(f"/questions/{question_id}").json()

    assert english["options"] == ["Mars", "Venus", "Jupiter", "Saturn"]
    assert spanish["options"] == [
        "es:Mars",
        "es:Venus",
        "es:Jupiter",
        "es:Saturn",
    ]
    assert spanish["answer"] == "es:Mars"


def test_random_question_uses_category_and_returns_api_format(client):
    created = client.post(
        "/questions",
        json={
            "question": "Which planet is known as the Red Planet?",
            "answer": "Mars",
            "category": "ciencia",
            "source": "OpenTriviaQA: science-technology",
        },
    )
    question_id = created.json()["id"]
    db_generator = app.dependency_overrides[get_db]()
    db: Session = next(db_generator)
    try:
        question = db.query(Question).filter(Question.id == question_id).one()
        question.options = [
            QuestionOption(position=index, text=option)
            for index, option in enumerate(["Mars", "Venus"])
        ]
        db.commit()
    finally:
        db.close()
        db_generator.close()

    response = client.get("/questions/random/ciencia?lang=en")

    assert response.status_code == 200
    assert response.json() == {
        "id": question_id,
        "question": "Which planet is known as the Red Planet?",
        "answer": "Mars",
        "category": "ciencia",
        "source": "OpenTriviaQA: science-technology",
        "options": ["Mars", "Venus"],
        "lang": "en",
    }


def test_random_question_returns_a_clear_error_for_empty_category(client):
    response = client.get("/questions/random/arte")

    assert response.status_code == 404
    assert "No hay preguntas disponibles" in response.json()["detail"]


def test_get_question_returns_the_original_language_when_requested(client):
    created = client.post(
        "/questions",
        json={
            "question": "Who wrote Hamlet?",
            "answer": "William Shakespeare",
        },
    )

    body = client.get(f"/questions/{created.json()['id']}?lang=en").json()

    assert body["lang"] == "en"
    assert body["question"] == "Who wrote Hamlet?"
    assert body["answer"] == "William Shakespeare"
    assert "William Shakespeare" in body["options"]
    assert {"Cordoba", "Rosario", "Mendoza"}.issubset(set(body["options"]))


def test_get_question_rejects_an_unsupported_language(client):
    created = client.post(
        "/questions",
        json={"question": "Who wrote Hamlet?", "answer": "William Shakespeare"},
    )

    response = client.get(f"/questions/{created.json()['id']}?lang=fr")

    assert response.status_code == 422
