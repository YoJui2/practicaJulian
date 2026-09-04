import pytest


@pytest.mark.parametrize(
    "payload",
    [
        {"answer": "An answer"},
        {"question": "A question"},
        {"question": "", "answer": "An answer"},
        {"question": "A question", "answer": ""},
        {"question": 123, "answer": "An answer"},
        {"question": "A question", "answer": 456},
    ],
)
def test_create_question_rejects_invalid_required_fields(client, payload):
    response = client.post("/questions", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field, limit",
    [("category", 100), ("source", 255)],
)
def test_create_question_rejects_fields_over_max_length(client, field, limit):
    payload = {
        "question": "A question",
        "answer": "An answer",
        field: "x" * (limit + 1),
    }

    response = client.post("/questions", json=payload)

    assert response.status_code == 422


def test_create_question_accepts_valid_payload(client):
    response = client.post(
        "/questions",
        json={
            "question": "  A question  ",
            "answer": "  An answer  ",
            "category": "history",
            "source": "book",
        },
    )

    assert response.status_code == 201
    assert response.json()["question"] == "  A question  "


def test_get_missing_question_returns_not_found_message(client):
    response = client.get("/questions/999")

    assert response.status_code == 200
    assert response.json() == {"error": "Pregunta no encontrada"}
