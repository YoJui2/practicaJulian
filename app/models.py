from app.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


CAREQA_ES_DATASET = "careqa-es"


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    source = Column(String(255), nullable=True)
    dataset_choices = Column(JSON, nullable=True)

    categorizations = relationship(
        "Categorization",
        back_populates="question",
        cascade="all, delete-orphan",
    )
    translations = relationship(
        "Translation",
        back_populates="question",
        cascade="all, delete-orphan",
    )


class Categorization(Base):
    """
    Registra la categorización de cada pregunta.
    Guarda tanto las decisiones automáticas de la IA como las manuales del humano.
    """
    __tablename__ = "categorizations"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    category_name = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=False, default=0.0)
    is_automatic = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    question = relationship("Question", back_populates="categorizations")


class Translation(Base):
    """
    Guarda la traducción de una pregunta y su respuesta a un idioma.
    """
    __tablename__ = "translations"
    __table_args__ = (
        UniqueConstraint("question_id", "lang", name="uix_question_lang"),
    )

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    lang = Column(String(10), nullable=False)
    question_translated = Column(Text, nullable=False)
    answer_translated = Column(Text, nullable=False)
    is_automatic = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    question = relationship("Question", back_populates="translations")