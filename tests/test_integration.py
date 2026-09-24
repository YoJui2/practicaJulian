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
    assert body["answer"] == "William Shakespeare"
    assert len(body["options"]) == 4
    assert len(set(body["options"])) == 4
    assert "William Shakespeare" in body["options"]
    assert {"Cordoba", "Rosario", "Mendoza"}.issubset(set(body["options"]))
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
    assert body["answer"] == "Respuesta Unica"
    assert "Respuesta Unica" in body["options"]
    assert {"Cordoba", "Rosario", "Mendoza"}.issubset(set(body["options"]))
