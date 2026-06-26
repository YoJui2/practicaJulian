"""
Módulo de clasificación de texto usando IA.

Este módulo provee dos estrategias de clasificación:
1. Zero-shot classification con transformers (más preciso, más lento)
2. Sentence embeddings + similitud coseno (más rápido, menos preciso)

TAREA: Implementar la clase AIClassifier con los métodos indicados.
"""
from dataclasses import dataclass


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

    TAREA: Implementar los métodos __init__, classify, y classify_batch.

    Ejemplo de uso esperado:
        classifier = AIClassifier(model_name="facebook/bart-large-mnli")
        result = classifier.classify(
            text="¿Qué es el overfitting?",
            candidate_labels=["machine_learning", "historia", "geografía"]
        )
        print(result.category_name)       # "machine_learning"
        print(result.confidence_score)    # 0.92
    """

    def __init__(self, model_name: str = "facebook/bart-large-mnli"):
        """
        Inicializa el clasificador cargando el modelo de Hugging Face.

        Args:
            model_name: nombre del modelo en Hugging Face Hub.

        TODO:
        - Importar pipeline de transformers
        - Crear self.pipeline usando pipeline("zero-shot-classification", model=model_name)
        - Guardar el model_name como atributo

        Pista: La carga del modelo puede tardar la primera vez (descarga ~1.5GB).
               Mostrá un print indicando que se está cargando.
        """
        # TODO: Implementar
        pass

    def classify(self, text: str, candidate_labels: list[str]) -> ClassificationResult:
        """
        Clasifica un texto individual contra una lista de categorías candidatas.

        Args:
            text: el texto a clasificar (ej. una pregunta)
            candidate_labels: lista de categorías posibles

        Returns:
            ClassificationResult con la categoría ganadora, su score, y todos los scores.

        TODO:
        - Llamar a self.pipeline(text, candidate_labels=candidate_labels)
        - El resultado del pipeline tiene:
            result["labels"]  → lista de categorías ordenadas por score (desc)
            result["scores"]  → lista de scores correspondientes
        - Construir y retornar un ClassificationResult con:
            category_name = result["labels"][0]  (la de mayor score)
            confidence_score = result["scores"][0]
            all_scores = dict(zip(result["labels"], result["scores"]))
        """
        # TODO: Implementar
        pass

    def classify_batch(self, texts: list[str], candidate_labels: list[str]) -> list[ClassificationResult]:
        """
        Clasifica múltiples textos contra las mismas categorías candidatas.

        Args:
            texts: lista de textos a clasificar
            candidate_labels: lista de categorías posibles

        Returns:
            Lista de ClassificationResult, uno por cada texto.

        TODO:
        - Iterar sobre cada texto y llamar a self.classify()
        - Retornar la lista de resultados
        - (Bonus) Investigar si el pipeline soporta batching nativo
          pasando una lista de textos directamente
        """
        # TODO: Implementar
        pass