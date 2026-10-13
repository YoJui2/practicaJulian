import argparse
import ast
import json
import os
import tempfile

import pandas as pd
import requests
from sqlalchemy import delete

from app.database import SessionLocal, engine
from app.data_quality import MAX_QUESTION_LENGTH
from app.models import Base, Categorization, Question, QuestionOption, Translation

DATASET_URL = (
    "https://huggingface.co/api/datasets/basicv8vc/SimpleQA/parquet/default/test/0.parquet"
)
OPENTRIVIA_DATASET_URL = (
    "https://huggingface.co/api/datasets/kth8/OpenTriviaQA/parquet/default/train"
)
OPENTRIVIA_CATEGORY_MAP = {
    "history": "historia",
    "sports": "deportes",
    "geography": "geografia",
    "literature": "arte",
    "entertainment": "entretenimiento",
    "movies": "entretenimiento",
    "television": "entretenimiento",
    "video-games": "entretenimiento",
    "celebrities": "entretenimiento",
    "science-technology": "ciencia",
}


def _metadata_as_dict(meta) -> dict:
    if meta is None or (isinstance(meta, float) and pd.isna(meta)):
        return {}
    if isinstance(meta, dict):
        return meta
    if isinstance(meta, str):
        s = meta.strip()
        if not s:
            return {}
        try:
            parsed = json.loads(s)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(s)
                return parsed if isinstance(parsed, dict) else {}
            except (ValueError, SyntaxError):
                return {}
    if hasattr(meta, "as_py"):
        v = meta.as_py()
        return v if isinstance(v, dict) else {}
    try:
        return dict(meta)
    except (TypeError, ValueError):
        return {}


def simpleqa_row_to_fields(row) -> dict | None:
    """SimpleQA parquet: columns problem, answer, metadata {topic, urls, ...}."""
    q = row.get("problem") or row.get("question") or ""
    a = row.get("answer") or row.get("answer_alias") or ""
    q = " ".join(str(q).split()) if pd.notna(q) else ""
    a = str(a).strip() if pd.notna(a) else ""
    if not q or len(q) > MAX_QUESTION_LENGTH or not a:
        return None

    meta = _metadata_as_dict(row.get("metadata"))
    topic = meta.get("topic")
    category = str(topic)[:100] if topic is not None and str(topic).strip() else None

    source = None
    urls = meta.get("urls")
    if isinstance(urls, (list, tuple)) and urls:
        first = urls[0]
        if first is not None and pd.notna(first) and str(first).strip():
            source = str(first).strip()[:255]

    return {"question": q, "answer": a, "category": category, "source": source}


def download_parquet(url: str) -> str:
    print(f"Descargando {url}...")
    r = requests.get(url, stream=True, timeout=(10, 120))
    r.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".parquet")
    tmp.write(r.content)
    tmp.close()
    return tmp.name


def _metadata_as_dict(meta) -> dict:
    """SimpleQA guarda `metadata` como dict, string JSON o repr estilo Python."""
    if meta is None or (isinstance(meta, float) and pd.isna(meta)):
        return {}
    if isinstance(meta, dict):
        return meta
    if isinstance(meta, str):
        s = meta.strip()
        if not s:
            return {}
        try:
            parsed = json.loads(s)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(s)
                return parsed if isinstance(parsed, dict) else {}
            except (ValueError, SyntaxError):
                return {}
    if hasattr(meta, "as_py"):
        v = meta.as_py()
        return v if isinstance(v, dict) else {}
    try:
        return dict(meta)
    except (TypeError, ValueError):
        return {}


def simpleqa_row_to_fields(row) -> dict | None:
    """Mapea Parquet SimpleQA → modelo Question (problem → question, topic → category)."""
    q = row.get("problem") or row.get("question") or ""
    a = row.get("answer") or ""
    q = " ".join(str(q).split()) if pd.notna(q) else ""
    a = str(a).strip() if pd.notna(a) else ""
    if not q or len(q) > MAX_QUESTION_LENGTH or not a:
        return None

    meta = _metadata_as_dict(row.get("metadata"))
    topic = meta.get("topic")
    category = (
        str(topic)[:100]
        if topic is not None and str(topic).strip()
        else None
    )

    source = None
    urls = meta.get("urls")
    if isinstance(urls, (list, tuple)) and urls:
        first = urls[0]
        if first is not None and pd.notna(first) and str(first).strip():
            source = str(first).strip()[:255]

    return {
        "question": q,
        "answer": a,
        "category": category,
        "source": source,
    }


def opentrivia_row_to_fields(row) -> dict | None:
    """Adapta una fila OpenTriviaQA al formato local conservando sus opciones."""
    question = _clean_dataset_text(row.get("question"))
    answer = _clean_dataset_text(row.get("answer"))
    raw_choices = row.get("choices")

    if not question or len(question) > MAX_QUESTION_LENGTH or not answer:
        return None

    if hasattr(raw_choices, "tolist"):
        raw_choices = raw_choices.tolist()
    elif isinstance(raw_choices, str):
        try:
            raw_choices = json.loads(raw_choices)
        except json.JSONDecodeError:
            try:
                raw_choices = ast.literal_eval(raw_choices)
            except (ValueError, SyntaxError):
                return None

    if not question or not answer or not isinstance(raw_choices, (list, tuple)):
        return None

    choices = []
    seen_choices = set()
    for raw_choice in raw_choices:
        choice = _clean_dataset_text(raw_choice)
        if not choice:
            return None
        normalized = " ".join(choice.split()).casefold()
        if normalized not in seen_choices:
            choices.append(choice)
            seen_choices.add(normalized)

    if len(choices) < 2:
        return None

    answer_key = " ".join(answer.split()).casefold()
    correct_choice = next(
        (
            choice
            for choice in choices
            if " ".join(choice.split()).casefold() == answer_key
        ),
        None,
    )
    if correct_choice is None:
        return None

    source_category = _clean_dataset_text(row.get("category")).casefold()
    return {
        "question": question,
        "answer": correct_choice,
        "options": choices,
        "category": OPENTRIVIA_CATEGORY_MAP.get(source_category),
        "source": f"OpenTriviaQA: {source_category}"[:255],
    }


def _clean_dataset_text(value) -> str:
    if value is None:
        return ""
    if not isinstance(value, (list, tuple, dict)) and pd.isna(value):
        return ""
    return " ".join(str(value).split())


def load_questions():
    Base.metadata.create_all(bind=engine)

    parquet_path = download_parquet(DATASET_URL)
    df = pd.read_parquet(parquet_path)
    os.unlink(parquet_path)

    print(f"Columnas disponibles: {list(df.columns)}")
    print(f"Filas: {len(df)}")
    print(df.head(3))

    session = SessionLocal()
    inserted = 0
    try:
        res = session.execute(delete(Question))
        removed = res.rowcount if res.rowcount is not None else 0
        print(f"Filas previas eliminadas: {removed}")

        for _, row in df.iterrows():
            fields = simpleqa_row_to_fields(row)
            if fields is None:
                continue
            session.add(Question(**fields))
            inserted += 1

        session.commit()
        print(f"Se insertaron {inserted} preguntas correctamente.")
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()


def _download_opentrivia_frames() -> pd.DataFrame:
    response = requests.get(OPENTRIVIA_DATASET_URL, timeout=(10, 60))
    response.raise_for_status()
    parquet_urls = response.json()
    if not isinstance(parquet_urls, list) or not parquet_urls:
        raise ValueError("Hugging Face no devolvió archivos Parquet para OpenTriviaQA")

    frames = []
    for url in parquet_urls:
        parquet_path = download_parquet(url)
        try:
            frames.append(pd.read_parquet(parquet_path))
        finally:
            os.unlink(parquet_path)
    return pd.concat(frames, ignore_index=True)


def load_opentrivia_questions() -> None:
    """Reemplaza las preguntas actuales por OpenTriviaQA y conserva sus opciones."""
    Base.metadata.create_all(bind=engine)
    df = _download_opentrivia_frames()
    session = SessionLocal()
    inserted = 0
    skipped = 0
    try:
        session.execute(delete(QuestionOption))
        session.execute(delete(Categorization))
        session.execute(delete(Translation))
        session.execute(delete(Question))

        for _, row in df.iterrows():
            fields = opentrivia_row_to_fields(row)
            if fields is None:
                skipped += 1
                continue

            options = fields.pop("options")
            category = fields["category"]
            question = Question(
                **fields,
                options=[
                    QuestionOption(position=position, text=option)
                    for position, option in enumerate(options)
                ],
            )
            if category is not None:
                question.categorizations.append(
                    Categorization(
                        category_name=category,
                        confidence_score=1.0,
                        is_automatic=True,
                    )
                )
            session.add(question)
            inserted += 1

            if inserted % 500 == 0:
                session.flush()

        session.commit()
        print(f"Se insertaron {inserted} preguntas de OpenTriviaQA.")
        print(f"Se omitieron {skipped} filas inválidas.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Carga un dataset de preguntas")
    parser.add_argument(
        "--dataset",
        choices=("simpleqa", "opentriviaqa"),
        default="opentriviaqa",
        help="dataset a importar (por defecto: opentriviaqa)",
    )
    return parser


if __name__ == "__main__":
    selected_dataset = build_argument_parser().parse_args().dataset
    if selected_dataset == "opentriviaqa":
        load_opentrivia_questions()
    else:
        load_questions()
