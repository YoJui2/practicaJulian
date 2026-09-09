import pandas as pd


REQUIRED_COLUMNS = {"patient_id", "date", "age"}


def assert_medical_schema(frame: pd.DataFrame) -> None:
    assert REQUIRED_COLUMNS.issubset(frame.columns)
    assert frame["patient_id"].notna().all()
    assert frame["date"].notna().all()
    assert pd.api.types.is_integer_dtype(frame["patient_id"])


def assert_valid_age_distribution(frame: pd.DataFrame) -> None:
    assert frame["age"].between(0, 120, inclusive="neither").all()


def test_medical_data_passes_schema_and_range_checks():
    frame = pd.DataFrame(
        {"patient_id": [101, 102], "date": ["2026-09-01", "2026-09-02"], "age": [35, 72]}
    )

    assert_medical_schema(frame)
    assert_valid_age_distribution(frame)


def test_medical_data_detects_missing_critical_values():
    frame = pd.DataFrame(
        {"patient_id": [101, None], "date": ["2026-09-01", None], "age": [35, 72]}
    )

    assert not frame["patient_id"].notna().all()
    assert not frame["date"].notna().all()