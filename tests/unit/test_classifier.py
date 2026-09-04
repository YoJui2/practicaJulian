from app.classifier import AIClassifier, ClassificationResult


def test_classify_maps_pipeline_result(monkeypatch):
    calls = []

    def fake_pipeline(task, model):
        assert task == "zero-shot-classification"
        assert model == "test-model"

        def classify(text, candidate_labels):
            calls.append((text, candidate_labels))
            return {
                "labels": ["science_and_technology", "history"],
                "scores": [0.91, 0.09],
            }

        return classify

    monkeypatch.setattr("app.classifier.pipeline", fake_pipeline)
    classifier = AIClassifier(model_name="test-model")

    result = classifier.classify("¿Qué es la gravedad?", ["science_and_technology", "history"])

    assert result == ClassificationResult(
        category_name="science_and_technology",
        confidence_score=0.91,
        all_scores={"science_and_technology": 0.91, "history": 0.09},
    )
    assert calls == [("¿Qué es la gravedad?", ["science_and_technology", "history"])]


def test_classify_batch_classifies_each_text(monkeypatch):
    monkeypatch.setattr("app.classifier.pipeline", lambda task, model: None)
    classifier = AIClassifier(model_name="test-model")
    expected_results = [
        ClassificationResult("history", 0.8, {"history": 0.8}),
        ClassificationResult("music", 0.7, {"music": 0.7}),
    ]
    calls = []

    def fake_classify(text, candidate_labels):
        calls.append((text, candidate_labels))
        return expected_results[len(calls) - 1]

    monkeypatch.setattr(classifier, "classify", fake_classify)
    labels = ["history", "music"]

    results = classifier.classify_batch(["Pregunta 1", "Pregunta 2"], labels)

    assert results == expected_results
    assert calls == [("Pregunta 1", labels), ("Pregunta 2", labels)]
