"""Run the end-to-end Parquet data quality pipeline."""
import argparse
import json
from pathlib import Path
import pandas as pd
from .ingestion import read_parquet_files
from .schema_validator import validate_schema, validate_records
from .transformer import transform
from .logger import get_logger


def run_pipeline(input_dir="data/input", output_dir="data/processed", quarantine_dir="data/quarantine", report_dir="reports"):
    output = Path(output_dir); quarantine_dir = Path(quarantine_dir); reports = Path(report_dir)
    output.mkdir(parents=True, exist_ok=True); quarantine_dir.mkdir(parents=True, exist_ok=True); reports.mkdir(parents=True, exist_ok=True)
    logger = get_logger(report_dir)
    batches = read_parquet_files(input_dir)
    if not batches:
        raise FileNotFoundError(f"No Parquet files found in {input_dir}. Run python scripts/generate_sample_data.py first.")
    accepted_frames, rejected_frames, details = [], [], []
    total = 0
    for path, frame in batches:
        total += len(frame)
        schema = validate_schema(frame)
        if not schema["valid"]:
            rejected = frame.copy(); rejected["_quarantine_reason"] = "; ".join(schema["issues"])
            rejected_frames.append(rejected)
            details.append({"file": path.name, "rows": len(frame), "accepted": 0, "quarantined": len(frame), **schema})
            logger.error("Rejected %s: %s", path.name, schema["issues"]); continue
        clean, bad = validate_records(frame)
        if not clean.empty: accepted_frames.append(transform(clean))
        if not bad.empty: rejected_frames.append(bad)
        details.append({"file": path.name, "rows": len(frame), "accepted": len(clean), "quarantined": len(bad), **schema})
        logger.info("Processed %s", path.name)
    accepted = pd.concat(accepted_frames, ignore_index=True) if accepted_frames else pd.DataFrame()
    rejected = pd.concat(rejected_frames, ignore_index=True) if rejected_frames else pd.DataFrame()
    clean_path = output / "cleaned_data.parquet"; bad_path = quarantine_dir / "quarantine.parquet"
    if not accepted.empty: accepted.to_parquet(clean_path, index=False)
    if not rejected.empty: rejected.to_parquet(bad_path, index=False)
    report = {"input_files": len(batches), "total_rows": total, "accepted_rows": len(accepted), "quarantined_rows": len(rejected), "reconciliation_passed": total == len(accepted) + len(rejected), "files": details, "outputs": {"cleaned_data": str(clean_path) if not accepted.empty else None, "quarantine": str(bad_path) if not rejected.empty else None}}
    (reports / "pipeline_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    logger.info("Completed: accepted=%s quarantined=%s", len(accepted), len(rejected))
    return report


def main():
    parser = argparse.ArgumentParser(description="YottaFlex Parquet pipeline")
    parser.add_argument("--input", default="data/input"); parser.add_argument("--output", default="data/processed")
    parser.add_argument("--quarantine", default="data/quarantine"); parser.add_argument("--reports", default="reports")
    args = parser.parse_args()
    print(json.dumps(run_pipeline(args.input, args.output, args.quarantine, args.reports), indent=2))

if __name__ == "__main__":
    main()
