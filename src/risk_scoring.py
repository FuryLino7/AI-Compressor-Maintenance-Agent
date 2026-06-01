import pandas as pd


def get_risk_level(score: int) -> str:
    if score >= 11:
        return "Critical"
    if score >= 7:
        return "High"
    if score >= 4:
        return "Medium"
    return "Low"


def has_recent_corrective_maintenance(maintenance_history: pd.DataFrame) -> bool:
    """
    Простая проверка: если в истории есть Corrective,
    добавляем небольшой риск.
    """
    if maintenance_history.empty:
        return False

    return maintenance_history["maintenance_type"].str.lower().eq("corrective").any()


def calculate_risk_score(
    latest_data: dict,
    trends: dict,
    asset_context: dict,
    production_context: dict,
    maintenance_history: pd.DataFrame,
) -> dict:
    score = 0
    risk_factors = []

    vibration = latest_data.get("vibration_mm_s", 0)
    oil_temp = latest_data.get("oil_temperature_c", 0)
    motor_temp = latest_data.get("motor_temperature_c", 0)
    efficiency = latest_data.get("efficiency_percent", 100)
    pressure = latest_data.get("discharge_pressure_bar", 10)

    power_trend = trends.get("power_consumption_change_percent", 0)

    criticality = asset_context.get("criticality", "Low")
    downtime_cost = production_context.get(
        "estimated_downtime_cost_eur_per_hour",
        0
    )

    # Vibration
    if vibration > 6.0:
        score += 4
        risk_factors.append("Very high vibration")
    elif vibration > 4.5:
        score += 3
        risk_factors.append("High vibration")

    # Oil temperature
    if oil_temp > 90:
        score += 3
        risk_factors.append("Very high oil temperature")
    elif oil_temp > 80:
        score += 2
        risk_factors.append("High oil temperature")

    # Motor temperature
    if motor_temp > 95:
        score += 3
        risk_factors.append("Very high motor temperature")
    elif motor_temp > 85:
        score += 2
        risk_factors.append("High motor temperature")

    # Efficiency
    if efficiency < 80:
        score += 3
        risk_factors.append("Critical efficiency drop")
    elif efficiency < 85:
        score += 2
        risk_factors.append("Efficiency below expected threshold")

    # Pressure
    if pressure < 7.0:
        score += 3
        risk_factors.append("Very low discharge pressure")
    elif pressure < 7.5:
        score += 2
        risk_factors.append("Low discharge pressure")

    # Power consumption trend
    if power_trend > 10:
        score += 2
        risk_factors.append("Power consumption increased by more than 10%")

    # Asset criticality
    if criticality == "High":
        score += 2
        risk_factors.append("High asset criticality")

    # Maintenance history
    if has_recent_corrective_maintenance(maintenance_history):
        score += 1
        risk_factors.append("Recent corrective maintenance history")

    # Business context
    if downtime_cost > 4000:
        score += 2
        risk_factors.append("High downtime cost per hour")

    risk_level = get_risk_level(score)

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "risk_details": [
        {"factor": "High vibration", "points": 3},
        {"factor": "High oil temperature", "points": 2},
        {"factor": "High asset criticality", "points": 2},
]
    }