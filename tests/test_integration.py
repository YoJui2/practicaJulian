def test_question_lifecycle_and_statistics(client):
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

    retrieved = client.get(f"/questions/{question_id}")
    assert retrieved.status_code == 200
    assert retrieved.json()["answer"] == "William Shakespeare"

    stats = client.get("/stats")
    assert stats.json() == {"total": 1, "by_category": {"history": 1}}


def test_category_stats_and_category_filter_use_categorizations(client):
    created = client.post(
        "/questions",
        json={"question": "Question", "answer": "Answer", "category": "general"},
    ).json()

    from app.models import Categorization
    from app.main import get_db

    db_dependency = client.app.dependency_overrides[get_db]
    db = next(db_dependency())
    db.add(
        Categorization(
            question_id=created["id"],
            category_name="science_and_technology",
            confidence_score=0.91,
            is_automatic=True,
        )
    )
    db.commit()
    db.close()

    filtered = client.get("/questions/category/science_and_technology")
    assert filtered.status_code == 200
    assert filtered.json()[0]["categorization"]["is_automatic"] is True

    stats = client.get("/categories/stats")
    assert stats.json()["total_questions"] == 1
    assert stats.json()["categorized"] == 1
    assert stats.json()["uncategorized"] == 0
    assert stats.json()["automatic"] == 1
    assert stats.json()["manual"] == 0
