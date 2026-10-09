import argparse
import ast
import json
import os
import tempfile

import pandas as pd
import requests
from sqlalchemy import text

from app.database import SessionLocal, engine, ensure_database_schema
from app.models import CAREQA_ES_DATASET, Question

CAREQA_DATASET = "careqa"
SIMPLEQA_DATASET = "simpleqa"
DEFAULT_DATASET = CAREQA_DATASET
DATASET_ENDPOINTS = {
    CAREQA_DATASET: (
        "https://huggingface.co/api/datasets/"
        "HPAI-BSC/CareQA/parquet/CareQA_es/test"
    ),
}
SIMPLEQA_PARQUET_URL = (
    "https://huggingface.co/api/datasets/basicv8vc/SimpleQA/"
    "parquet/default/test/0.parquet"
)


def _metadata_as_dict(meta) -> dict:
    if meta is None or (isinstance(meta, float) and pd.isna(meta)):
        return {}
    if isinstance(meta, dict):
        return meta
    if isinstance(meta, str):
        try:
            parsed = json.loads(meta.strip())
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(meta.strip())
                if isinstance(parsed, dict):
                    return parsed
            except (ValueError, SyntaxError):
                pass
    if hasattr(meta, "as_py"):
        parsed = meta.as_py()
        return parsed if isinstance(parsed, dict) else {}
    try:
        return dict(meta)
    except (TypeError, ValueError):
        return {}


def simpleqa_row_to_fields(row) -> dict | None:
    """Mapea una fila SimpleQA al modelo Question."""
    question = row.get("problem") or row.get("question") or ""
    answer = row.get("answer") or row.get("answer_alias") or ""
    question = str(question).strip() if pd.notna(question) else ""
    answer = str(answer).strip() if pd.notna(answer) else ""
    if not question or not answer:
        return None

    metadata = _metadata_as_dict(row.get("metadata"))
    topic = metadata.get("topic")
    category = str(topic)[:100] if topic is not None else None
    source = None
    urls = metadata.get("urls")
    if isinstance(urls, (list, tuple)) and urls:
        first = urls[0]
        if first is not None and pd.notna(first) and str(first).strip():
            source = str(first).strip()[:255]

    return {
        "question": question,
        "answer": answer,
        "category": category,
        "source": source,
    }


def careqa_row_to_fields(row) -> dict | None:
    """Convierte las columnas question/op1-op4/cop de CareQA al esquema local."""
    question = row.get("question")
    if not isinstance(question, str) or not question.strip():
        return None

    choices = [row.get(f"op{index}") for index in range(1, 5)]
    if not all(isinstance(choice, str) and choice.strip() for choice in choices):
        return None

    try:
        correct_index = int(row.get("cop"))
    except (TypeError, ValueError, OverflowError):
        return None
    if correct_index != row.get("cop") or not 1 <= correct_index <= 4:
        return None

    normalized_choices = [" ".join(choice.split()) for choice in choices]
    if len({choice.casefold() for choice in normalized_choices}) != 4:
        return None

    category = row.get("category")
    category = str(category).strip()[:100] if pd.notna(category) else None
    return {
        "question": " ".join(question.split()),
        "answer": normalized_choices[correct_index - 1],
        "category": category or None,
        "source": CAREQA_ES_DATASET,
        "dataset_choices": normalized_choices,
    }


def _parquet_urls(dataset: str) -> list[str]:
    if dataset == SIMPLEQA_DATASET:
        return [SIMPLEQA_PARQUET_URL]

    response = requests.get(DATASET_ENDPOINTS[dataset], timeout=(10, 60))
    response.raise_for_status()
    urls = response.json()
    if not isinstance(urls, list) or not urls or not all(
        isinstance(url, str) and url.startswith("https://") for url in urls
    ):
        raise ValueError(f"Hugging Face devolvió una lista de Parquet inválida: {urls!r}")
    return urls


def download_parquet(url: str) -> str:
    print(f"Descargando {url}...")
    response = requests.get(url, timeout=(10, 60))
    response.raise_for_status()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".parquet") as tmp:
        tmp.write(response.content)
        return tmp.name


def load_questions(dataset: str = DEFAULT_DATASET) -> int:
    """Reemplaza las preguntas por el dataset seleccionado."""
    if dataset not in {*DATASET_ENDPOINTS, SIMPLEQA_DATASET}:
        raise ValueError(f"Dataset no soportado: {dataset}")

    ensure_database_schema(engine)
    row_mapper = careqa_row_to_fields if dataset == CAREQA_DATASET else simpleqa_row_to_fields
    imported_rows: list[dict] = []
    total_rows = 0

    for url in _parquet_urls(dataset):
        parquet_path = download_parquet(url)
        try:
            frame = pd.read_parquet(parquet_path)
        finally:
            os.unlink(parquet_path)

        print(f"Columnas disponibles: {list(frame.columns)}")
        print(f"Filas: {len(frame)}")
        total_rows += len(frame)
        for _, row in frame.iterrows():
            fields = row_mapper(row)
            if fields is not None:
                imported_rows.append(fields)

    if not imported_rows:
        raise ValueError(
            f"No se importó ninguna fila válida de {dataset}; "
            "la base existente no se modificó."
        )

    session = SessionLocal()
    try:
        session.execute(text("TRUNCATE TABLE questions RESTART IDENTITY CASCADE"))
        session.add_all(Question(**fields) for fields in imported_rows)
        session.commit()
        print(
            f"Se insertaron {len(imported_rows)} preguntas de {dataset}; "
            f"se omitieron {total_rows - len(imported_rows)} filas inválidas."
        )
        return len(imported_rows)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga preguntas desde Hugging Face.")
    parser.add_argument(
        "--dataset",
        choices=[CAREQA_DATASET, SIMPLEQA_DATASET],
        default=DEFAULT_DATASET,
        help="Dataset a importar (predeterminado: CareQA en español).",
    )
    load_questions(parser.parse_args().dataset)


if __name__ == "__main__":
    main()
