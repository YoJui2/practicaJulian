from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://admin:admin123@localhost:5432/questions_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_database_schema(bind) -> None:
    """Create tables and add dataset columns to existing question tables."""
    Base.metadata.create_all(bind=bind)
    if "questions" not in inspect(bind).get_table_names():
        return

    columns = {
        column["name"] for column in inspect(bind).get_columns("questions")
    }
    if "dataset_choices" not in columns:
        with bind.begin() as connection:
            connection.execute(
                text("ALTER TABLE questions ADD COLUMN dataset_choices JSON")
            )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()