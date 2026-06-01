from pathlib import Path

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