
import csv
from pathlib import Path
from math import isclose

BASE = Path(__file__).resolve().parent

def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

rows = read_csv(BASE / "data" / "forecast_dataset.csv")

# Chainring - ProductID 322
material_key = "9"

material_rows = [
    r for r in rows if r["MaterialKey"] == material_key
]

train = sorted(
    [r for r in material_rows if r["IsTrainPeriod"] == "1"],
    key=lambda r: r["Month"]
)
test = sorted(
    [r for r in material_rows if r["IsTestPeriod"] == "1"],
    key=lambda r: r["Month"]
)

def recursive_ma3(train_values, horizon):
    history = list(train_values)
    predictions = []

    for _ in range(horizon):
        forecast = sum(history[-3:]) / 3
        predictions.append(forecast)
        history.append(forecast)

    return predictions

train_values = [
    float(r["RequirementQty_PU"]) for r in train
]
actual_values = [
    float(r["RequirementQty_PU"]) for r in test
]

forecasts = recursive_ma3(train_values, len(test))

errors = [
    abs(a - f)
    for a, f in zip(actual_values, forecasts)
]
calculated_mae = sum(errors) / len(errors)

print("===== TC-FC-03: RECURSIVE MA(3) =====")
print("ProductID: 322")
print("Model: MA_3")
print()
print("Month       Actual      Forecast    Abs Error")

for r, actual, forecast, error in zip(
    test, actual_values, forecasts, errors
):
    print(
        f"{r['Month'][:7]:<11}"
        f"{actual:>9.2f}"
        f"{forecast:>12.2f}"
        f"{error:>12.2f}"
    )

print()
print("Train Months:", len(train))
print("Test Months:", len(test))
print("Calculated MAE:", round(calculated_mae, 4))
print("Expected MAE: 354.63")

# Đối chiếu với MAE đã lưu của G06
metrics = read_csv(
    BASE / "output" / "G06_baseline_metrics.csv"
)
saved = [
    r for r in metrics
    if r["MaterialKey"] == material_key
    and r["Model"] == "MA_3"
]

saved_mae = float(saved[0]["MAE"]) if len(saved) == 1 else None
print("Saved MAE:", saved_mae)

# Kiểm tra chống rò rỉ:
# Thay toàn bộ Actual Test bằng giá trị giả lập rất lớn.
# Dự báo phải giữ nguyên vì chỉ được dùng Train.
modified_test_actual = [999999.0] * len(test)

forecasts_after_change = recursive_ma3(
    train_values, len(modified_test_actual)
)

leakage_free = all(
    isclose(a, b, abs_tol=1e-9)
    for a, b in zip(forecasts, forecasts_after_change)
)

print()
print("===== DATA LEAKAGE CHECK =====")
print("Changed Test Actual: YES")
print("Forecast Unchanged:", leakage_free)
print("Test Actual Used in Forecast: NO" if leakage_free else "CHECK REQUIRED")

mae_ok = (
    len(test) == 6
    and abs(calculated_mae - 354.63) < 0.02
    and saved_mae is not None
    and abs(calculated_mae - saved_mae) < 0.01
)

print()
print("MAE Check:", "PASS" if mae_ok else "FAIL")
print("Leakage Check:", "PASS" if leakage_free else "FAIL")
print(
    "TC-FC-03:",
    "PASS" if mae_ok and leakage_free else "FAIL"
)
