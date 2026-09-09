def test_questions_require_non_empty_question_and_answer(client):
    response = client.post(
        "/questions",
        json={"question": "", "answer": "An answer"},
    )

    assert response.status_code == 422


def test_missing_question_returns_a_clear_error(client):
    response = client.get("/questions/999")

    assert response.status_code == 200
    assert response.json() == {"error": "Pregunta no encontrada"}