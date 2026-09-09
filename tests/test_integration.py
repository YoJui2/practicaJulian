def test_create_and_list_questions_use_the_database(client):
    response = client.post(
        "/questions",
        json={
            "question": "What is an API?",
            "answer": "A contract for communication between software components.",
            "category": "software",
        },
    )

    assert response.status_code == 201
    created = response.json()
    assert created["id"] == 1

    listed = client.get("/questions")
    assert listed.status_code == 200
    assert listed.json()[0]["question"] == "What is an API?"


def test_category_filter_and_stats_are_consistent(client):
    for category in ("testing", "testing", "data"):
        client.post(
            "/questions",
            json={"question": f"Question {category}", "answer": "Answer", "category": category},
        )

    assert len(client.get("/questions/category/testing").json()) == 2
    assert client.get("/stats").json() == {
        "total": 3,
        "by_category": {"testing": 2, "data": 1},
    }