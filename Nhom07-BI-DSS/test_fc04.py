
import csv
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent

def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

dataset = read_csv(BASE / "data" / "forecast_dataset.csv")
selection = read_csv(BASE / "output" / "G11_model_selection.csv")

dataset_keys = {r["MaterialKey"] for r in dataset}
selection_keys = [r["MaterialKey"] for r in selection]

selected = [
    r for r in selection
    if r["SelectionStatus"] == "SELECTED"
]

not_selected = [
    r for r in selection
    if r["SelectionStatus"] != "SELECTED"
]

model_counts = Counter(r["SelectedModel"] for r in selected)

valid_models = {"ETS_Seasonal", "MA_6", "ARIMA", "MA_3"}

invalid_selected = [
    r for r in selected
    if r["SelectedModel"] not in valid_models
    or any(
        not r[field].strip()
        for field in ["MAE", "RMSE", "Bias"]
    )
]

print("===== TC-FC-04: G11 MODEL SELECTION =====")
print("Dataset Materials:", len(dataset_keys))
print("G11 Rows:", len(selection))
print("Selected Materials:", len(selected))
print("Not Selected Materials:", len(not_selected))
print("Duplicate MaterialKeys:",
      len(selection_keys) - len(set(selection_keys)))
print("Dataset/G11 Key Match:",
      set(selection_keys) == dataset_keys)

print("\n===== SELECTED MODEL DISTRIBUTION =====")
for model, count in sorted(model_counts.items()):
    print(f"{model}: {count}")

print("\n===== MATERIALS WITHOUT VALID MODEL =====")
for r in not_selected:
    print(
        "MaterialKey:", r["MaterialKey"],
        "| Status:", r["SelectionStatus"],
        "| SelectedModel:", r["SelectedModel"] or "N/A"
    )

passed = (
    len(dataset_keys) == 35
    and len(selection) == 35
    and len(selected) == 34
    and len(not_selected) == 1
    and len(selection_keys) == len(set(selection_keys))
    and set(selection_keys) == dataset_keys
    and not invalid_selected
    and model_counts == {
        "ETS_Seasonal": 28,
        "MA_6": 3,
        "ARIMA": 2,
        "MA_3": 1
    }
)

print("\nG11 Selection Check:",
      "PASS" if passed else "FAIL")
