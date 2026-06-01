from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
np.random.seed(42)

START_TIME = datetime(2026, 5, 1, 0, 0)
HOURS = 7 * 24  # 7 days of hourly data


# ------------------------------------------------------------
# Static enterprise-style data
# ------------------------------------------------------------
def generate_asset_master() -> pd.DataFrame:
    data = [
        {
            "asset_id": "COMP-01",
            "asset_name": "Main Air Compressor 1",
            "asset_type": "Industrial Air Compressor",
            "plant": "Plant A",
            "location": "Packaging Line 2",
            "criticality": "High",
            "manufacturer": "Atlas Copco",
            "installation_year": 2019,
        },
        {
            "asset_id": "COMP-02",
            "asset_name": "Backup Air Compressor 2",
            "asset_type": "Industrial Air Compressor",
            "plant": "Plant A",
            "location": "Packaging Line 2",
            "criticality": "Medium",
            "manufacturer": "Kaeser",
            "installation_year": 2021,
        },
        {
            "asset_id": "COMP-03",
            "asset_name": "Utility Compressor 3",
            "asset_type": "Industrial Air Compressor",
            "plant": "Plant B",
            "location": "Utilities Area",
            "criticality": "High",
            "manufacturer": "Ingersoll Rand",
            "installation_year": 2018,
        },
        {
            "asset_id": "COMP-04",
            "asset_name": "Assembly Compressor 4",
            "asset_type": "Industrial Air Compressor",
            "plant": "Plant A",
            "location": "Assembly Line 1",
            "criticality": "Medium",
            "manufacturer": "Atlas Copco",
            "installation_year": 2020,
        },
    ]

    return pd.DataFrame(data)


def generate_maintenance_history() -> pd.DataFrame:
    data = [
        {
            "work_order_id": "WO-1042",
            "asset_id": "COMP-01",
            "date": "2026-03-15",
            "maintenance_type": "Preventive",
            "issue_found": "Oil filter replacement",
            "downtime_hours": 2.0,
            "cost_eur": 850,
        },
        {
            "work_order_id": "WO-1098",
            "asset_id": "COMP-01",
            "date": "2026-04-20",
            "maintenance_type": "Corrective",
            "issue_found": "Bearing inspection",
            "downtime_hours": 5.0,
            "cost_eur": 2400,
        },
        {
            "work_order_id": "WO-1110",
            "asset_id": "COMP-02",
            "date": "2026-04-25",
            "maintenance_type": "Preventive",
            "issue_found": "General inspection",
            "downtime_hours": 1.5,
            "cost_eur": 600,
        },
        {
            "work_order_id": "WO-1132",
            "asset_id": "COMP-03",
            "date": "2026-05-02",
            "maintenance_type": "Corrective",
            "issue_found": "Pressure control valve inspection",
            "downtime_hours": 4.0,
            "cost_eur": 1800,
        },
        {
            "work_order_id": "WO-1150",
            "asset_id": "COMP-04",
            "date": "2026-04-12",
            "maintenance_type": "Preventive",
            "issue_found": "Cooling system cleaning",
            "downtime_hours": 2.5,
            "cost_eur": 1200,
        },
    ]

    return pd.DataFrame(data)


def generate_production_impact() -> pd.DataFrame:
    data = [
        {
            "asset_id": "COMP-01",
            "connected_process": "Packaging Line 2",
            "production_dependency": "High",
            "estimated_downtime_cost_eur_per_hour": 4500,
            "sla_impact": "High",
        },
        {
            "asset_id": "COMP-02",
            "connected_process": "Packaging Line 2",
            "production_dependency": "Medium",
            "estimated_downtime_cost_eur_per_hour": 2200,
            "sla_impact": "Medium",
        },
        {
            "asset_id": "COMP-03",
            "connected_process": "Plant Utilities",
            "production_dependency": "High",
            "estimated_downtime_cost_eur_per_hour": 6000,
            "sla_impact": "High",
        },
        {
            "asset_id": "COMP-04",
            "connected_process": "Assembly Line 1",
            "production_dependency": "Medium",
            "estimated_downtime_cost_eur_per_hour": 3000,
            "sla_impact": "Medium",
        },
    ]

    return pd.DataFrame(data)


# ------------------------------------------------------------
# Helper functions for sensor generation
# ------------------------------------------------------------
def add_noise(value: float, std: float) -> float:
    return value + np.random.normal(0, std)


def linear_increase(step: int, start_step: int, max_increase: float) -> float:
    """
    Возвращает постепенный рост после определенного момента.
    Например, если start_step = 120, то деградация начнется ближе к концу периода.
    """
    if step < start_step:
        return 0.0

    progress = (step - start_step) / max(1, HOURS - start_step - 1)
    return progress * max_increase


def linear_decrease(step: int, start_step: int, max_decrease: float) -> float:
    if step < start_step:
        return 0.0

    progress = (step - start_step) / max(1, HOURS - start_step - 1)
    return progress * max_decrease


# ------------------------------------------------------------
# Scenario generators
# ------------------------------------------------------------
def generate_normal_operation(asset_id: str, timestamp: datetime, step: int) -> dict:
    """
    COMP-02: нормальная работа.
    """
    return {
        "timestamp": timestamp,
        "asset_id": asset_id,
        "discharge_pressure_bar": round(add_noise(8.1, 0.08), 2),
        "air_flow_m3_min": round(add_noise(42.0, 0.5), 2),
        "motor_temperature_c": round(add_noise(74.0, 1.5), 1),
        "vibration_mm_s": round(add_noise(2.3, 0.25), 2),
        "oil_temperature_c": round(add_noise(68.0, 1.3), 1),
        "power_consumption_kw": round(add_noise(115.0, 2.0), 1),
        "load_percent": round(add_noise(76.0, 2.0), 1),
        "efficiency_percent": round(add_noise(91.0, 1.0), 1),
    }


def generate_bearing_degradation(asset_id: str, timestamp: datetime, step: int) -> dict:
    """
    COMP-01: главный проблемный сценарий.
    Постепенно растут вибрация, температура масла и двигателя.
    Эффективность падает, энергопотребление растет.
    """
    degradation_start = 100

    vibration_increase = linear_increase(step, degradation_start, 3.6)
    oil_temp_increase = linear_increase(step, degradation_start, 18.0)
    motor_temp_increase = linear_increase(step, degradation_start, 16.0)
    power_increase = linear_increase(step, degradation_start, 18.0)
    efficiency_drop = linear_decrease(step, degradation_start, 10.0)

    return {
        "timestamp": timestamp,
        "asset_id": asset_id,
        "discharge_pressure_bar": round(add_noise(8.0, 0.08), 2),
        "air_flow_m3_min": round(add_noise(41.8, 0.45), 2),
        "motor_temperature_c": round(add_noise(74.0 + motor_temp_increase, 1.2), 1),
        "vibration_mm_s": round(add_noise(2.2 + vibration_increase, 0.18), 2),
        "oil_temperature_c": round(add_noise(68.0 + oil_temp_increase, 1.0), 1),
        "power_consumption_kw": round(add_noise(115.0 + power_increase, 1.8), 1),
        "load_percent": round(add_noise(78.0, 1.8), 1),
        "efficiency_percent": round(add_noise(91.0 - efficiency_drop, 0.8), 1),
    }


def generate_air_leak_pressure_loss(asset_id: str, timestamp: datetime, step: int) -> dict:
    """
    COMP-03: проблема с давлением / возможная утечка воздуха.
    Давление падает, эффективность падает, энергопотребление растет.
    """
    issue_start = 95

    pressure_drop = linear_decrease(step, issue_start, 1.1)
    power_increase = linear_increase(step, issue_start, 16.0)
    efficiency_drop = linear_decrease(step, issue_start, 8.0)

    # Небольшая нестабильность расхода воздуха
    air_flow_instability = np.sin(step / 4) * 1.2 if step > issue_start else 0

    return {
        "timestamp": timestamp,
        "asset_id": asset_id,
        "discharge_pressure_bar": round(add_noise(8.2 - pressure_drop, 0.1), 2),
        "air_flow_m3_min": round(add_noise(42.5 + air_flow_instability, 0.6), 2),
        "motor_temperature_c": round(add_noise(76.0, 1.8), 1),
        "vibration_mm_s": round(add_noise(2.7, 0.3), 2),
        "oil_temperature_c": round(add_noise(70.0, 1.5), 1),
        "power_consumption_kw": round(add_noise(118.0 + power_increase, 2.2), 1),
        "load_percent": round(add_noise(80.0, 2.0), 1),
        "efficiency_percent": round(add_noise(90.0 - efficiency_drop, 1.0), 1),
    }


def generate_cooling_issue(asset_id: str, timestamp: datetime, step: int) -> dict:
    """
    COMP-04: перегрев / проблема с охлаждением.
    Растут температуры, нагрузка высокая, эффективность падает.
    """
    issue_start = 105

    motor_temp_increase = linear_increase(step, issue_start, 20.0)
    oil_temp_increase = linear_increase(step, issue_start, 17.0)
    efficiency_drop = linear_decrease(step, issue_start, 7.0)

    return {
        "timestamp": timestamp,
        "asset_id": asset_id,
        "discharge_pressure_bar": round(add_noise(8.0, 0.08), 2),
        "air_flow_m3_min": round(add_noise(41.5, 0.45), 2),
        "motor_temperature_c": round(add_noise(75.0 + motor_temp_increase, 1.4), 1),
        "vibration_mm_s": round(add_noise(2.8, 0.28), 2),
        "oil_temperature_c": round(add_noise(69.0 + oil_temp_increase, 1.2), 1),
        "power_consumption_kw": round(add_noise(117.0, 2.0), 1),
        "load_percent": round(add_noise(88.0, 2.0), 1),
        "efficiency_percent": round(add_noise(90.0 - efficiency_drop, 1.0), 1),
    }


def generate_sensor_readings() -> pd.DataFrame:
    rows = []

    scenario_map = {
        "COMP-01": generate_bearing_degradation,
        "COMP-02": generate_normal_operation,
        "COMP-03": generate_air_leak_pressure_loss,
        "COMP-04": generate_cooling_issue,
    }

    for asset_id, generator_func in scenario_map.items():
        for step in range(HOURS):
            timestamp = START_TIME + timedelta(hours=step)
            row = generator_func(asset_id, timestamp, step)
            rows.append(row)

    df = pd.DataFrame(rows)

    # Чтобы CSV был красиво отсортирован
    df = df.sort_values(["asset_id", "timestamp"]).reset_index(drop=True)

    return df


# ------------------------------------------------------------
# Main script
# ------------------------------------------------------------
def main() -> None:
    asset_master = generate_asset_master()
    sensor_readings = generate_sensor_readings()
    maintenance_history = generate_maintenance_history()
    production_impact = generate_production_impact()

    asset_master.to_csv(DATA_DIR / "asset_master.csv", index=False)
    sensor_readings.to_csv(DATA_DIR / "sensor_readings.csv", index=False)
    maintenance_history.to_csv(DATA_DIR / "maintenance_history.csv", index=False)
    production_impact.to_csv(DATA_DIR / "production_impact.csv", index=False)

    print("Synthetic data generated successfully.")
    print(f"Files saved to: {DATA_DIR}")
    print()
    print("Generated files:")
    print("- asset_master.csv")
    print("- sensor_readings.csv")
    print("- maintenance_history.csv")
    print("- production_impact.csv")
    print()
    print("Sensor readings shape:", sensor_readings.shape)


if __name__ == "__main__":
    main()