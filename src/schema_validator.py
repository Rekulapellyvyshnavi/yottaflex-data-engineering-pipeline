"""Schema and row-level data quality validation."""
import pandas as pd

REQUIRED_COLUMNS = {"record_id", "event_date", "amount", "category"}
OPTIONAL_COLUMNS = {"region", "source_system"}


def validate_schema(frame: pd.DataFrame) -> dict:
    issues = [f"Missing required column: {c}" for c in sorted(REQUIRED_COLUMNS - set(frame.columns))]
    drift = [f"New column detected: {c}" for c in frame.columns if c not in REQUIRED_COLUMNS | OPTIONAL_COLUMNS]
    drift += [f"Approved optional column present: {c}" for c in OPTIONAL_COLUMNS if c in frame.columns]
    return {"valid": not issues, "issues": issues, "drift": drift}


def validate_records(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    data = frame.copy()
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        data["_quarantine_reason"] = "Missing required column(s): " + ", ".join(sorted(missing))
        return data.iloc[0:0].copy(), data
    data["event_date"] = pd.to_datetime(data["event_date"], errors="coerce")
    data["amount"] = pd.to_numeric(data["amount"], errors="coerce")
    reasons = pd.Series("", index=data.index, dtype="object")
    reasons.loc[data["record_id"].isna()] += "invalid record_id; "
    reasons.loc[data["event_date"].isna()] += "invalid event_date; "
    reasons.loc[data["amount"].isna()] += "invalid amount; "
    empty_category = data["category"].isna() | data["category"].astype("string").str.strip().eq("").fillna(True)
    reasons.loc[empty_category] += "empty category; "
    clean = data.loc[reasons.eq("")].copy()
    bad = data.loc[~reasons.eq("")].copy()
    bad["_quarantine_reason"] = reasons.loc[bad.index]
    if not clean.empty:
        clean["record_id"] = pd.to_numeric(clean["record_id"]).astype("int64")
        clean["amount"] = clean["amount"].astype("float64")
    return clean, bad
