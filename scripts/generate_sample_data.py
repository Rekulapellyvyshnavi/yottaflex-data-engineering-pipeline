"""Generate sample Parquet batches with schema evolution and bad records."""
from pathlib import Path
import pandas as pd

out = Path("data/input"); out.mkdir(parents=True, exist_ok=True)
batch1 = pd.DataFrame({"record_id":[1001,1002,1003],"event_date":["2026-10-01","2026-10-02","2026-10-03"],"amount":[125.50,80.0,42.75],"category":["Retail","Travel","Retail"]})
batch2 = pd.DataFrame({"record_id":[1004,1005,1006],"event_date":["2026-10-04","not-a-date","2026-10-06"],"amount":[210.0,55.0,None],"category":["Utilities","Retail","Travel"],"region":["South","West","North"],"source_system":["ERP","CRM","ERP"]})
batch1.to_parquet(out / "batch_01.parquet", index=False)
batch2.to_parquet(out / "batch_02.parquet", index=False)
print(f"Sample files created in {out}")
