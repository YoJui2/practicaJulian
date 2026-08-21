"""
Módulo de clasificación de texto usando IA.

Este módulo provee dos estrategias de clasificación:
1. Zero-shot classification con transformers (más preciso, más lento)
2. Sentence embeddings + similitud coseno (más rápido, menos preciso)

TAREA: Implementar la clase AIClassifier con los métodos indicados.
"""
from dataclasses import dataclass
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

    def __init__(self, model_name: str = "facebook/bart-large-mnli"):  #Inicializa el clasificador cargando el modelo de Hugging Face.

        self.model_name = model_name
        print("Cargando modelo de IA...")
        self.pipeline = pipeline(
            "zero-shot-classification",
            model=model_name
        )
        print(f"Modelo cargado: {model_name}")

    def classify(self, text: str, candidate_labels: list[str]) -> ClassificationResult:  #Clasifica un texto individual contra una lista de categorías candidatas.

        result = self.pipeline(text, candidate_labels=candidate_labels)

        category_name = result["labels"][0]
        confidence_score = result["scores"][0]
        all_scores = dict(zip(result["labels"], result["scores"]))

        return ClassificationResult(
            category_name=category_name,
            confidence_score=confidence_score,
            all_scores=all_scores,
        )