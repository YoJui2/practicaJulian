from app.data_quality import MAX_QUESTION_LENGTH


def test_create_question_requires_question_and_answer(client):
    response = client.post("/questions", json={"question": "A question"})

    assert response.status_code == 422


def test_create_question_rejects_an_overly_long_category(client):
    payload = {
        "question": "A question",
        "answer": "An answer",
        "category": "x" * 101,
    }

    response = client.post("/questions", json=payload)

    assert response.status_code == 422


def test_create_question_rejects_question_over_character_limit(client):
    response = client.post(
        "/questions",
        json={
            "question": "q" * (MAX_QUESTION_LENGTH + 1),
            "answer": "An answer",
        },
    )

    assert response.status_code == 422


def test_create_question_rejects_true_false_answer(client):
    response = client.post(
        "/questions",
        json={"question": "Is this accurate?", "answer": "True"},
    )

    assert response.status_code == 422


def test_create_question_accepts_a_valid_payload(client):
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


def test_create_question_rejects_a_number_instead_of_text(client):
    response = client.post(
        "/questions",
        json={"question": 123, "answer": "An answer"},
    )

    assert response.status_code == 422


def test_get_missing_question_returns_a_not_found_error(client):
    response = client.get("/questions/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Pregunta no encontrada"}
