import json
from pathlib import Path

from sqlalchemy import delete

from app.database import SessionLocal, engine
from app.models import Base, Question

# URL Parquet Hugging Face (descomentá y usá el bloque de abajo en load_questions para volver a HF):
# DATASET_URL = (
#     "https://huggingface.co/api/datasets/basicv8vc/SimpleQA/parquet/default/test/0.parquet"
# )

DATA_JSON_PATH = Path(__file__).resolve().parent.parent / "data" / "preguntas_ejemplo.json"


def load_questions():
    Base.metadata.create_all(bind=engine)

    with DATA_JSON_PATH.open(encoding="utf-8") as f:
        rows = json.load(f)

    print(f"Origen: {DATA_JSON_PATH}")
    if rows:
        print(f"Claves de ejemplo: {list(rows[0].keys())}")
    print(f"Filas: {len(rows)}")
    print(rows[:3])

    # Carga alternativa: descomentá DATASET_URL y leé el Parquet con pandas/requests.

    session = SessionLocal()
    inserted = 0
    try:
        res = session.execute(delete(Question))
        removed = res.rowcount if res.rowcount is not None else 0
        print(f"Filas previas eliminadas: {removed}")

        for row in rows:
            question = Question(
                question=row.get("question", ""),
                answer=row.get("answer", "") or row.get("answer_alias", ""),
                category=row.get("category", None),
                source=row.get("source", None),
            )
            session.add(question)
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
