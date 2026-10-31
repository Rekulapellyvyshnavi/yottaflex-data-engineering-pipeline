import pandas as pd
from src.schema_validator import validate_schema, validate_records
from src.transformer import transform
from src.main import run_pipeline


def sample():
    return pd.DataFrame({"record_id":[1],"event_date":["2026-01-01"],"amount":[10.0],"category":["Retail"]})


def test_optional_columns_are_accepted():
    frame = sample(); frame["region"] = "South"
    assert validate_schema(frame)["valid"]


def test_missing_required_column_is_rejected():
    assert not validate_schema(sample().drop(columns=["amount"]))["valid"]


def test_invalid_rows_are_quarantined():
    frame = sample(); frame.loc[0,"event_date"] = "bad-date"
    clean, bad = validate_records(frame)
    assert clean.empty and len(bad) == 1
    assert "invalid event_date" in bad.iloc[0]["_quarantine_reason"]


def test_transform_normalizes_values():
    result = transform(sample())
    assert result.iloc[0]["category"] == "retail"
    assert result.iloc[0]["region"] == "unknown"


def test_pipeline_reconciles_rows(tmp_path):
    inp = tmp_path / "input"; inp.mkdir()
    frame = sample(); frame.loc[1 if len(frame)>1 else 0, "event_date"] = "2026-01-01"
    frame.to_parquet(inp / "batch.parquet", index=False)
    report = run_pipeline(inp, tmp_path/"out", tmp_path/"bad", tmp_path/"reports")
    assert report["reconciliation_passed"]
    assert report["accepted_rows"] + report["quarantined_rows"] == report["total_rows"]
