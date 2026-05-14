import ast
import json
import os
import tempfile

import pandas as pd
import requests
from app.database import SessionLocal, engine
from app.models import Base, Question

DATASET_URL = (
    "https://huggingface.co/api/datasets/basicv8vc/SimpleQA/parquet/default/test/0.parquet"
)


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
    q = str(q).strip() if pd.notna(q) else ""
    a = str(a).strip() if pd.notna(a) else ""
    if not q or not a:
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
    r = requests.get(url, stream=True)
    r.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".parquet")
    tmp.write(r.content)
    tmp.close()
    return tmp.name


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


if __name__ == "__main__":
    load_questions()