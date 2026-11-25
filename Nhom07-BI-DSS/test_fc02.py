
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent
PRED_FILE = BASE / "output" / "G06_baseline_predictions.csv"
METRIC_FILE = BASE / "output" / "G06_baseline_metrics.csv"

def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

# ProductID 322 tương ứng MaterialKey 9
material_key = "9"
model = "Naive"

predictions = [
    r for r in read_csv(PRED_FILE)
    if r["MaterialKey"] == material_key
    and r["Model"] == model
]
predictions.sort(key=lambda r: r["ForecastMonth"])

metrics = [
    r for r in read_csv(METRIC_FILE)
    if r["MaterialKey"] == material_key
    and r["Model"] == model
]

print("===== TC-FC-02: NAIVE FORECAST VALIDATION =====")
print("ProductID: 322 | MaterialKey: 9")
print("Model: Naive")
print()
print("Month       Actual      Forecast    Abs Error")

absolute_errors = []

for r in predictions:
    actual = float(r["ActualQty"])
    forecast = float(r["ForecastQty"])
    abs_error = abs(actual - forecast)
    absolute_errors.append(abs_error)

    print(
        f"{r['ForecastMonth'][:7]:<11} "
        f"{actual:>9.2f} "
        f"{forecast:>12.2f} "
        f"{abs_error:>12.2f}"
    )

calculated_mae = (
    sum(absolute_errors) / len(absolute_errors)
    if absolute_errors else None
)

saved_mae = float(metrics[0]["MAE"]) if len(metrics) == 1 else None

print()
print("Test Months:", len(predictions))
print("Calculated MAE:", calculated_mae)
print("Saved MAE:", saved_mae)

forecast_ok = (
    len(predictions) == 6
    and all(
        abs(float(r["ForecastQty"]) - 1108.75) < 0.0001
        for r in predictions
    )
)
mae_ok = (
    calculated_mae is not None
    and saved_mae is not None
    and abs(calculated_mae - 380.50) < 0.01
    and abs(calculated_mae - saved_mae) < 0.01
)

# Đối chiếu Forecast Naive với Actual cuối tập Train
dataset = read_csv(BASE / "data" / "forecast_dataset.csv")
train = sorted(
    [
        r for r in dataset
        if r["MaterialKey"] == material_key
        and r["IsTrainPeriod"] == "1"
    ],
    key=lambda r: r["Month"]
)
last_train = train[-1] if train else None
last_train_actual = (
    float(last_train["RequirementQty_PU"])
    if last_train else None
)

print("Last Train Month:", last_train["Month"] if last_train else "N/A")
print("Last Train Actual:", last_train_actual)

baseline_ok = (
    last_train_actual is not None
    and abs(last_train_actual - 1108.75) < 0.0001
)

passed = forecast_ok and mae_ok and baseline_ok

print("TC-FC-02:", "PASS" if passed else "FAIL")
