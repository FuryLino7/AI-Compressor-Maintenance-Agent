from pathlib import Path
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def load_asset_master() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "asset_master.csv")


def load_sensor_readings() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "sensor_readings.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def load_maintenance_history() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "maintenance_history.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_production_impact() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "production_impact.csv")


def load_all_data() -> dict:
    return {
        "asset_master": load_asset_master(),
        "sensor_readings": load_sensor_readings(),
        "maintenance_history": load_maintenance_history(),
        "production_impact": load_production_impact(),
    }

def calculate_metric_trends(
    df: pd.DataFrame,
    metrics: list[str] | None = None,
    time_col: str = "timestamp",
    window: int = 24,
) -> dict:
    """
    Calculates simple trend indicators for compressor sensor metrics.

    Returns a dictionary like:
    {
        "temperature_c": {
            "current": 78.2,
            "previous": 77.5,
            "delta": 0.7,
            "delta_pct": 0.9,
            "slope": 0.12,
            "trend": "increasing"
        }
    }
    """

    if df is None or df.empty:
        return {}

    data = df.copy()

    if time_col in data.columns:
        data[time_col] = pd.to_datetime(data[time_col], errors="coerce")
        data = data.sort_values(time_col)

    exclude_cols = {
        time_col,
        "asset_id",
        "equipment_id",
        "machine_id",
        "compressor_id",
        "status",
        "risk_level",
        "failure_mode",
        "recommendation",
    }

    if metrics is None:
        metrics = [
            col
            for col in data.columns
            if col not in exclude_cols and pd.api.types.is_numeric_dtype(data[col])
        ]

    trends = {}

    recent_data = data.tail(window)

    for metric in metrics:
        if metric not in recent_data.columns:
            continue

        series = pd.to_numeric(recent_data[metric], errors="coerce").dropna()

        if len(series) == 0:
            continue

        current = float(series.iloc[-1])

        if len(series) >= 2:
            previous = float(series.iloc[-2])
            delta = current - previous

            if previous != 0:
                delta_pct = (delta / previous) * 100
            else:
                delta_pct = 0.0
        else:
            previous = current
            delta = 0.0
            delta_pct = 0.0

        if len(series) >= 3:
            x = np.arange(len(series))
            slope = float(np.polyfit(x, series.values, 1)[0])
        else:
            slope = 0.0

        mean_abs = max(abs(series.mean()), 1)
        threshold = mean_abs * 0.01

        if slope > threshold:
            trend = "increasing"
        elif slope < -threshold:
            trend = "decreasing"
        else:
            trend = "stable"

        trends[metric] = {
            "current": round(current, 3),
            "previous": round(previous, 3),
            "delta": round(delta, 3),
            "delta_pct": round(delta_pct, 2),
            "slope": round(slope, 4),
            "trend": trend,
        }

    return trends