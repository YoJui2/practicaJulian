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
    assert retrieved.json()["answer"] == "William Shakespeare"
    assert retrieved.headers["access-control-allow-origin"] == (
        "http://localhost:5173"
    )

    stats = client.get("/stats")
    assert stats.json() == {"total": 1, "by_category": {"history": 1}}
