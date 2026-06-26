from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db, engine
from app.models import Base, Question

app = FastAPI(title="Questions API", version="1.0.0")


class QuestionCreate(BaseModel):
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    category: str | None = Field(None, max_length=100)
    source: str | None = Field(None, max_length=255)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "message": "Questions API funcionando",
        "endpoints": [
            "/questions",
            "POST /questions",
            "/questions/{id}",
            "/questions/category/{category}",
            "/stats",
        ],
        "docs": "/docs",
    }


@app.get("/questions")
def list_questions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    questions = db.query(Question).offset(skip).limit(limit).all()
    return questions


@app.post("/questions", status_code=201)
def create_question(payload: QuestionCreate, db: Session = Depends(get_db)):
    db_question = Question(
        question=payload.question,
        answer=payload.answer,
        category=payload.category,
        source=payload.source,
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


@app.get("/questions/category/{category}")
def list_questions_by_category(
    category: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    questions = (
        db.query(Question)
        .filter(Question.category == category)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return questions


@app.get("/stats")
def stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Question.id)).scalar() or 0
    rows = (
        db.query(Question.category, func.count(Question.id))
        .group_by(Question.category)
        .order_by(func.count(Question.id).desc())
        .all()
    )
    by_category = {
        (cat if cat is not None else "(sin categoría)"): count for cat, count in rows
    }
    return {"total": total, "by_category": by_category}


@app.get("/questions/{question_id}")
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        return {"error": "Pregunta no encontrada"}
    return question

# --- Agregar estos endpoints al archivo main.py existente ---


@app.get("/questions/category/{category_name}")
def list_by_category(category_name: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Retorna las preguntas que fueron categorizadas con una categoría específica.

    TAREA:
    - Hacer un JOIN entre Question y Categorization
    - Filtrar por Categorization.category_name == category_name
    - Aplicar skip y limit
    - Retornar las preguntas con su información de categorización

    TODO: Implementar la query con JOIN.
    """
    # TODO: Implementar
    pass


@app.get("/categories")
def list_categories():
    """
    Retorna la lista de categorías disponibles.

    TAREA:
    - Importar CATEGORIES desde app/categories.py
    - Retornar la lista completa

    TODO: Implementar.
    """
    # TODO: Implementar
    pass


@app.get("/categories/stats")
def category_stats(db: Session = Depends(get_db)):
    """
    Retorna estadísticas de categorización.

    Debe retornar un JSON como:
    {
        "total_questions": 1000,
        "categorized": 850,
        "uncategorized": 150,
        "automatic": 700,
        "manual": 150,
        "by_category": {
            "machine_learning": 200,
            "historia": 150,
            ...
        }
    }

    TAREA:
    - Contar el total de preguntas
    - Contar las categorizadas (que tienen entrada en categorizations)
    - Contar automáticas vs manuales
    - Agrupar por categoría (GROUP BY)

    TODO: Implementar las queries necesarias.
    Pista: usá db.query(func.count(...)).group_by(...)
    """
    # TODO: Implementar
    pass
