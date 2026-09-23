from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db, engine
from app.models import Base, Categorization, Question
from app.categories import CATEGORIES


class QuestionCreate(BaseModel):
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    category: str | None = Field(None, max_length=100)
    source: str | None = Field(None, max_length=255)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Questions API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["Accept", "Content-Type"],
    allow_credentials=False,
)


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


@app.get("/questions/category/{category_name}")
def list_by_category(
    category_name: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Question, Categorization)
        .join(Categorization, Categorization.question_id == Question.id)
        .filter(Categorization.category_name == category_name)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": question.id,
            "question": question.question,
            "answer": question.answer,
            "category": question.category,
            "source": question.source,
            "categorization": {
                "id": categorization.id,
                "category_name": categorization.category_name,
                "confidence_score": categorization.confidence_score,
                "is_automatic": categorization.is_automatic,
                "created_at": categorization.created_at,
            },
        }
        for question, categorization in rows
    ]


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


@app.get("/categories")
def list_categories():
    return CATEGORIES


@app.get("/categories/stats")
def category_stats(db: Session = Depends(get_db)):
    total_questions = db.query(func.count(Question.id)).scalar() or 0

    categorized = (
        db.query(func.count(func.distinct(Categorization.question_id)))
        .scalar()
        or 0
    )

    automatic = (
        db.query(func.count(Categorization.id))
        .filter(Categorization.is_automatic.is_(True))
        .scalar()
        or 0
    )

    manual = (
        db.query(func.count(Categorization.id))
        .filter(Categorization.is_automatic.is_(False))
        .scalar()
        or 0
    )

    rows = (
        db.query(
            Categorization.category_name,
            func.count(Categorization.id),
        )
        .group_by(Categorization.category_name)
        .order_by(func.count(Categorization.id).desc())
        .all()
    )

    by_category = {
        category_name: count
        for category_name, count in rows
    }

    return {
        "total_questions": total_questions,
        "categorized": categorized,
        "uncategorized": total_questions - categorized,
        "automatic": automatic,
        "manual": manual,
        "by_category": by_category,
    }
