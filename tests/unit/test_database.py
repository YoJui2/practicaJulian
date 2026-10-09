from sqlalchemy import create_engine, inspect, text

from app.database import ensure_database_schema


def test_ensure_database_schema_adds_choices_to_existing_questions_table():
    engine = create_engine("sqlite://")
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE TABLE questions ("
                    "id INTEGER PRIMARY KEY, "
                    "question TEXT NOT NULL, "
                    "answer TEXT NOT NULL, "
                    "category VARCHAR(100), "
                    "source VARCHAR(255))"
                )
            )

        ensure_database_schema(engine)

        column_names = {
            column["name"] for column in inspect(engine).get_columns("questions")
        }
        assert "dataset_choices" in column_names
    finally:
        engine.dispose()
