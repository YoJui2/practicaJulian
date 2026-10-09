import pytest
from fastapi import HTTPException

from app.database import get_db
from app.models import CAREQA_ES_DATASET, Question


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


def test_get_careqa_question_returns_saved_spanish_options(client, monkeypatch):
    def unexpected_generation(*args, **kwargs):
        raise AssertionError(
            f"CareQA no debe generar ni traducir opciones: {args!r}, {kwargs!r}"
        )

    monkeypatch.setattr("app.main.build_options", unexpected_generation)
    monkeypatch.setattr("app.main.translate_question", unexpected_generation)
    created = client.post(
        "/questions",
        json={
            "question": "¿Qué recomienda el protocolo?",
            "answer": "La opción correcta",
            "category": "Medicine",
            "source": CAREQA_ES_DATASET,
        },
    )
    assert created.status_code == 201

    question_id = created.json()["id"]
    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    try:
        question = db.query(Question).filter(Question.id == question_id).first()
        question.dataset_choices = [
            "La opción correcta",
            "Alternativa dos",
            "Alternativa tres",
            "Alternativa cuatro",
        ]
        db.commit()
    finally:
        db_generator.close()

    response = client.get(f"/questions/{question_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": question_id,
        "question": "¿Qué recomienda el protocolo?",
        "answer": "La opción correcta",
        "category": "Medicine",
        "source": CAREQA_ES_DATASET,
        "options": [
            "La opción correcta",
            "Alternativa dos",
            "Alternativa tres",
            "Alternativa cuatro",
        ],
        "lang": "es",
    }


def test_get_careqa_question_rejects_english(client):
    created = client.post(
        "/questions",
        json={
            "question": "¿Qué recomienda el protocolo?",
            "answer": "La opción correcta",
            "source": CAREQA_ES_DATASET,
        },
    )

    response = client.get(f"/questions/{created.json()['id']}?lang=en")

    assert response.status_code == 422


def test_careqa_options_fail_if_missing_or_invalid():
    from app.main import _dataset_options

    invalid_question = Question(
        question="Pregunta",
        answer="Correcta",
        source=CAREQA_ES_DATASET,
        dataset_choices=["Correcta", "Incorrecta"],
    )

    with pytest.raises(HTTPException) as error:
        _dataset_options(invalid_question)

    assert error.value.status_code == 500
