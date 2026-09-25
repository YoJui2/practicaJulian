import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base


class _FakeTextGenerator:
    def __call__(self, prompt, **kwargs):
        return [{"generated_text": "Cordoba; Rosario; Mendoza"}]


class _FakeTranslationTokenizer:
    def __call__(self, texts, **kwargs):
        return {"input_ids": list(texts)}

    def decode(self, sequence, **kwargs):
        return f"es:{sequence[0]}"


class _FakeTranslationModel:
    def generate(self, **kwargs):
        return [[text] for text in kwargs["input_ids"]]


@pytest.fixture(autouse=True)
def fake_options_generator(monkeypatch):
    monkeypatch.setattr(
        "app.options._get_generator",
        lambda: _FakeTextGenerator(),
    )


@pytest.fixture(autouse=True)
def fake_translator(monkeypatch):
    monkeypatch.setattr("app.translator._cache", {})
    monkeypatch.setattr(
        "app.translator._get_translator",
        lambda: (_FakeTranslationTokenizer(), _FakeTranslationModel()),
    )


@pytest.fixture
def client(monkeypatch):
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr("app.main.engine", test_engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
