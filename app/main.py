from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db, engine
from app.data_quality import (
    MAX_QUESTION_LENGTH,
    TRUE_FALSE_ANSWERS,
    is_true_false_question,
)
from app.models import Base, Categorization, Question, QuestionOption
from app.categories import CATEGORIES
from app.live_translation import translate_question
from app.options import build_options
from app.translator import DEFAULT_SOURCE_LANG, DEFAULT_TARGET_LANG


class QuestionCreate(BaseModel):
    question: str = Field(..., min_length=1, max_length=MAX_QUESTION_LENGTH)
    answer: str = Field(..., min_length=1)
    category: str | None = Field(None, max_length=100)
    source: str | None = Field(None, max_length=255)

    @field_validator("answer")
    @classmethod
    def reject_true_false_answer(cls, answer: str) -> str:
        if is_true_false_question(answer, []):
            raise ValueError("No se permiten preguntas de verdadero o falso.")
        return answer


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


def _format_question(question: Question, lang: Literal["es", "en"]) -> dict:
    source_options = [option.text for option in question.options] or None

    if lang == DEFAULT_SOURCE_LANG:
        return {
            "id": question.id,
            "question": question.question,
            "answer": question.answer,
            "category": question.category,
            "source": question.source,
            "options": source_options
            or build_options(question.question, question.answer),
            "lang": DEFAULT_SOURCE_LANG,
        }

    translated = translate_question(
        question.question,
        question.answer,
        options=source_options,
        target_lang=lang,
    )
    return {
        "id": question.id,
        "question": translated["question"],
        "answer": translated["answer"],
        "category": question.category,
        "source": question.source,
        "options": translated["options"],
        "lang": translated["lang"],
    }


@app.get("/questions/random/{category_name}")
def get_random_question(
    category_name: str,
    lang: Literal["es", "en"] = DEFAULT_TARGET_LANG,
    db: Session = Depends(get_db),
):
    question = (
        db.query(Question)
        .filter(
            (Question.category == category_name)
            | Question.categorizations.any(
                Categorization.category_name == category_name
            ),
            func.length(func.trim(Question.question)) <= MAX_QUESTION_LENGTH,
            func.lower(func.trim(func.trim(Question.answer), ".!?")).notin_(
                TRUE_FALSE_ANSWERS
            ),
            ~(
                Question.options.any(
                    func.lower(
                        func.trim(func.trim(QuestionOption.text), ".!?")
                    ).in_(("true", "verdadero", "verdadera"))
                )
                & Question.options.any(
                    func.lower(
                        func.trim(func.trim(QuestionOption.text), ".!?")
                    ).in_(("false", "falso", "falsa"))
                )
                & ~Question.options.any(
                    ~func.lower(
                        func.trim(func.trim(QuestionOption.text), ".!?")
                    ).in_(
                        (
                            "true",
                            "false",
                            "verdadero",
                            "verdadera",
                            "falso",
                            "falsa",
                        )
                    )
                )
            ),
        )
        .order_by(func.random())
        .first()
    )
    if question is None:
        raise HTTPException(
            status_code=404,
            detail=f"No hay preguntas disponibles para la categoría {category_name}.",
        )
    return _format_question(question, lang)


@app.get("/questions/{question_id}")
def get_question(
    question_id: int,
    lang: Literal["es", "en"] = DEFAULT_TARGET_LANG,
    db: Session = Depends(get_db),
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")

    return _format_question(question, lang)


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
