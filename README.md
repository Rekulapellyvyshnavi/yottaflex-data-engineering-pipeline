# YottaFlex Data Engineering Pipeline

A Python-based Parquet pipeline that demonstrates batch ingestion, schema evolution awareness, record-level data quality validation, quarantine handling, transformations, reconciliation, reporting, and automated tests.

## Features
- Reads multiple Parquet batches from an input directory.
- Detects missing required fields, approved optional fields, and unexpected columns.
- Validates record IDs, event dates, numeric amounts, and categories.
- Sends invalid records to a quarantine Parquet file with a reason.
- Standardizes category and region values.
- Writes clean Parquet output and a JSON run report.
- Logs pipeline activity.
- Includes Pytest tests and GitHub Actions CI.

## Project structure
```
.
├── .github/workflows/tests.yml
├── data/
│   ├── input/          # Sample Parquet batches generated here
│   ├── processed/      # Clean output created at runtime
│   └── quarantine/     # Rejected records created at runtime
├── reports/            # JSON report and log created at runtime
├── scripts/
│   └── generate_sample_data.py
├── src/
│   ├── drift_detector.py
│   ├── ingestion.py
│   ├── logger.py
│   ├── main.py
│   ├── schema_validator.py
│   └── transformer.py
├── tests/
│   └── test_pipeline.py
└── requirements.txt
```

## Requirements
- Python 3.10 or newer
- pandas
- pyarrow
- pytest (for tests)

## Setup
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 1. Generate sample input data
```bash
python scripts/generate_sample_data.py
```
This creates two Parquet batches. The second batch includes optional schema fields and deliberately invalid records to demonstrate quarantine.

## 2. Run the pipeline
```bash
python -m src.main
```
Custom directories can be provided:
```bash
python -m src.main --input data/input --output data/processed --quarantine data/quarantine --reports reports
```

## 3. Run automated tests
```bash
pytest -q
```

## Output files
- `data/processed/cleaned_data.parquet` — validated and standardized rows.
- `data/quarantine/quarantine.parquet` — invalid rows and their quarantine reasons.
- `reports/pipeline_report.json` — file-level row counts, schema findings, and reconciliation result.
- `reports/pipeline.log` — execution log.

The reconciliation check confirms that input rows equal accepted rows plus quarantined rows.
