"""Preparacion del dataset supervisado a partir de revisiones humanas."""

from dataclasses import dataclass
import pickle
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import Categorization, Question


@dataclass(frozen=True)
class TrainingExample:
    """Ejemplo etiquetado que puede usarse para entrenar un clasificador."""

    text: str
    label: str
    question_id: int


@dataclass(frozen=True)
class TrainingReport:
    """Resultado del entrenamiento y metricas de validacion."""

    model_path: Path
    training_examples: int
    validation_examples: int
    metrics: dict[str, object]


def load_manual_examples(db: Session) -> list[TrainingExample]:
    """Carga preguntas cuya etiqueta fue confirmada por una persona.

    Se toma la categorizacion manual mas reciente por pregunta para evitar
    duplicar ejemplos cuando una pregunta fue revisada mas de una vez.
    """
    categorizations = (
        db.query(Categorization)
        .join(Question)
        .filter(
            Categorization.is_automatic.is_(False),
            Question.question.is_not(None),
            Question.question != "",
        )
        .order_by(Categorization.question_id, Categorization.created_at.desc(), Categorization.id.desc())
        .all()
    )

    examples: list[TrainingExample] = []
    seen_question_ids: set[int] = set()
    for categorization in categorizations:
        if categorization.question_id in seen_question_ids:
            continue

        question = categorization.question
        text = question.question.strip()
        if not text:
            continue

        examples.append(
            TrainingExample(
                text=text,
                label=categorization.category_name,
                question_id=question.id,
            )
        )
        seen_question_ids.add(categorization.question_id)

    return examples


def split_training_data(
    examples: list[TrainingExample],
    validation_size: float = 0.2,
    random_state: int = 42,
) -> tuple[list[TrainingExample], list[TrainingExample]]:
    """Divide ejemplos en entrenamiento y validacion de forma reproducible."""
    if not examples:
        raise ValueError("No hay ejemplos manuales para entrenar")
    if not 0 < validation_size < 1:
        raise ValueError("validation_size debe estar entre 0 y 1")

    labels = {example.label for example in examples}
    if len(labels) < 2:
        raise ValueError("Se necesitan al menos dos categorias manuales")

    from sklearn.model_selection import train_test_split

    minimum_validation_fraction = len(labels) / len(examples)
    effective_validation_size = max(validation_size, minimum_validation_fraction)

    train, validation = train_test_split(
        examples,
        test_size=effective_validation_size,
        random_state=random_state,
        stratify=[example.label for example in examples],
    )
    return list(train), list(validation)


def train_model(
    db: Session,
    model_path: str | Path = "models/modelomainv1.pkl",
    validation_size: float = 0.2,
    random_state: int = 42,
) -> TrainingReport:
    """Entrena y guarda modelomainv1 usando exclusivamente revisiones humanas."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report

    examples = load_manual_examples(db)
    train, validation = split_training_data(
        examples,
        validation_size=validation_size,
        random_state=random_state,
    )

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    features = vectorizer.fit_transform(example.text for example in train)
    classifier = LogisticRegression(max_iter=1000, random_state=random_state)
    classifier.fit(features, [example.label for example in train])

    validation_features = vectorizer.transform(example.text for example in validation)
    predictions = classifier.predict(validation_features)
    metrics = classification_report(
        [example.label for example in validation],
        predictions,
        output_dict=True,
        zero_division=0,
    )

    destination = Path(model_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as file:
        pickle.dump(
            {
                "model_name": "modelomainv1",
                "vectorizer": vectorizer,
                "classifier": classifier,
                "categories": sorted({example.label for example in examples}),
                "metrics": metrics,
            },
            file,
        )

    return TrainingReport(
        model_path=destination,
        training_examples=len(train),
        validation_examples=len(validation),
        metrics=metrics,
    )