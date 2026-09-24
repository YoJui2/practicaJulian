"""
Módulo de clasificación de texto usando IA.

Este módulo provee dos estrategias de clasificación:
1. Zero-shot classification con transformers (más preciso, más lento)
2. Sentence embeddings + similitud coseno (más rápido, menos preciso)

TAREA: Implementar la clase AIClassifier con los métodos indicados.
"""
from dataclasses import dataclass
import pickle
from pathlib import Path

from transformers import pipeline


@dataclass
class ClassificationResult:
    """
    Resultado de una clasificación.

    Atributos:
        category_name: nombre de la categoría asignada
        confidence_score: score de confianza (0.0 a 1.0)
        all_scores: diccionario con los scores de todas las categorías
    """
    category_name: str
    confidence_score: float
    all_scores: dict[str, float]


class AIClassifier:
    """
    Clasificador de texto basado en IA.

    Usa el pipeline zero-shot-classification de Hugging Face para asignar
    una categoría a un texto dado.
    """

    def __init__(
        self,
        model_name: str = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
        trained_model_path: str | Path = "models/modelomainv1.pkl",
    ):
        """Carga modelomainv1 si existe y usa zero-shot como fallback."""
        self.model_name = model_name
        self.trained_model_path = Path(trained_model_path)
        self.supervised_model = None

        if self.trained_model_path.exists():
            with self.trained_model_path.open("rb") as file:
                self.supervised_model = pickle.load(file)
            print(f"Modelo supervisado cargado: {self.trained_model_path}")
        else:
            print("Cargando modelo de IA...")
            self.pipeline = pipeline(
                "zero-shot-classification",
                model=model_name,
            )
            print(f"Modelo cargado: {model_name}")

    def classify(self, text: str, candidate_labels: list[str]) -> ClassificationResult:
        if self.supervised_model is not None:
            vectorizer = self.supervised_model["vectorizer"]
            classifier = self.supervised_model["classifier"]
            probabilities = classifier.predict_proba(vectorizer.transform([text]))[0]
            scores = dict(zip(classifier.classes_, probabilities))
            if candidate_labels:
                scores = {
                    label: float(scores.get(label, 0.0))
                    for label in candidate_labels
                }
            category_name, confidence_score = max(scores.items(), key=lambda item: item[1])
            return ClassificationResult(
                category_name=category_name,
                confidence_score=float(confidence_score),
                all_scores=scores,
            )

        result = self.pipeline(text, candidate_labels=candidate_labels)

        category_name = result["labels"][0]
        confidence_score = result["scores"][0]
        all_scores = dict(zip(result["labels"], result["scores"]))

        return ClassificationResult(
            category_name=category_name,
            confidence_score=confidence_score,
            all_scores=all_scores,
        )

    def classify_batch(self, texts: list[str], candidate_labels: list[str]) -> list[ClassificationResult]:
        """
        Clasifica múltiples textos contra las mismas categorías candidatas.
        """
        results: list[ClassificationResult] = []

        for text in texts:
            result = self.classify(text=text, candidate_labels=candidate_labels)
            results.append(result)

        return results