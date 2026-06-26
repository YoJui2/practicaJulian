
from app.database import Base
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    source = Column(String(255), nullable=True)

class Categorization(Base):
    """
    Registra la categorización de cada pregunta.
    Guarda tanto las decisiones automáticas de la IA como las manuales del humano.

    TAREA: Completar las columnas del modelo.

    Columnas requeridas:
    - id: clave primaria autoincremental (Integer)
    - question_id: FK a questions.id (Integer, ForeignKey)
    - category_name: nombre de la categoría asignada (String(100))
    - confidence_score: score de confianza de la IA, entre 0.0 y 1.0 (Float)
    - is_automatic: True si la IA decidió, False si decidió un humano (Boolean)
    - created_at: timestamp de cuándo se hizo la categorización (DateTime)

    Relación:
    - question: relación con el modelo Question (relationship)
    """
    __tablename__ = "categorizations"

    # TODO: Definir las columnas id, question_id, category_name,
    #       confidence_score, is_automatic, created_at.
    #
    # Pistas:
    #   - Usá ForeignKey("questions.id") para la FK
    #   - Usá default=True para is_automatic
    #   - Usá default=datetime.now(timezone.utc) o un callable para created_at
    #   - Definí una relationship("Question", backref="categorizations")

    pass