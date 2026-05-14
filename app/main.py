from pathlib import Path

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import get_db, engine
from app.models import Base, Question

app = FastAPI(title="Questions API", version="1.0.0")

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "message": "Questions API funcionando",
        "endpoints": ["/questions", "/questions/{id}"],
        "interfaz": "/interfaz/",
        "docs": "/docs",
    }


@app.get("/questions")
def list_questions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    questions = db.query(Question).offset(skip).limit(limit).all()
    return questions


@app.get("/questions/{question_id}")
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        return {"error": "Pregunta no encontrada"}
    return question


if _STATIC_DIR.is_dir():
    app.mount(
        "/interfaz",
        StaticFiles(directory=str(_STATIC_DIR), html=True),
        name="interfaz",
    )