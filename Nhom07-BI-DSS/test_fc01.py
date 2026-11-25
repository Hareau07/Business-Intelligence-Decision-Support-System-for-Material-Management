
import csv
from pathlib import Path

file_path = Path(r"D:\Nhom07-BI-DSS\data\forecast_dataset.csv")

with file_path.open("r", encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

materials = {r["MaterialKey"] for r in rows}
keys = [(r["MaterialKey"], r["Month"]) for r in rows]

train = [r for r in rows if r["IsTrainPeriod"] == "1"]
test = [r for r in rows if r["IsTestPeriod"] == "1"]

train_keys = {(r["MaterialKey"], r["Month"]) for r in train}
test_keys = {(r["MaterialKey"], r["Month"]) for r in test}

overlap = train_keys & test_keys
duplicate_count = len(keys) - len(set(keys))
unassigned = [
    r for r in rows
    if r["IsTrainPeriod"] != "1" and r["IsTestPeriod"] != "1"
]

print("===== TC-FC-01: FORECAST DATA VALIDATION =====")
print("Materials:", len(materials))
print("Total Observations:", len(rows))
print("Train Observations:", len(train))
print("Test Observations:", len(test))
print("Train/Test Overlap:", len(overlap))
print("Duplicate Material-Month:", duplicate_count)
print("Unassigned Observations:", len(unassigned))

passed = (
    len(materials) == 35
    and len(rows) == 1145
    and len(train) == 941
    and len(test) == 204
    and len(overlap) == 0
    and duplicate_count == 0
    and len(unassigned) == 0
)

print("TC-FC-01:", "PASS" if passed else "FAIL")
