import pandas as pd


def expected_downtime_by_risk(risk_level: str) -> int:
    """
    Простая и объяснимая оценка ожидаемого downtime по risk level.
    Для MVP лучше держать эту логику прозрачной.
    """
    if risk_level == "Critical":
        return 12
    if risk_level == "High":
        return 6
    if risk_level == "Medium":
        return 2
    return 0


def get_business_impact_text(risk_level: str) -> str:
    if risk_level == "Critical":
        return "High probability of unplanned compressor shutdown and production loss."
    if risk_level == "High":
        return "Significant risk of downtime or reduced production efficiency."
    if risk_level == "Medium":
        return "Possible degradation of compressor performance."
    return "No immediate business-critical impact detected."


def get_business_recommendation(risk_level: str) -> str:
    if risk_level == "Critical":
        return (
            "Inspect the compressor urgently, prepare maintenance resources, "
            "and reduce load or stop operation if the condition worsens."
        )
    if risk_level == "High":
        return (
            "Schedule maintenance as soon as possible and monitor compressor "
            "condition closely."
        )
    if risk_level == "Medium":
        return (
            "Plan preventive maintenance and continue monitoring key indicators."
        )
    return "Continue normal operation and regular monitoring."


def estimate_business_impact(
    asset_id: str,
    risk_level: str,
    production_impact_df: pd.DataFrame,
) -> dict:
    row = production_impact_df[
        production_impact_df["asset_id"] == asset_id
    ]

    if row.empty:
        return {
            "business_impact_level": risk_level,
            "connected_process": "Unknown",
            "downtime_cost_eur_per_hour": 0,
            "expected_downtime_hours": 0,
            "estimated_total_impact_eur": 0,
            "estimated_cost_eur": 0,
            "sla_impact": "Unknown",
            "production_impact": "No production impact context found.",
            "business_recommendation": "Review asset manually.",
        }

    context = row.iloc[0].to_dict()

    cost_per_hour = context["estimated_downtime_cost_eur_per_hour"]
    expected_hours = expected_downtime_by_risk(risk_level)
    estimated_total = cost_per_hour * expected_hours

    return {
        "business_impact_level": risk_level,
        "connected_process": context["connected_process"],
        "downtime_cost_eur_per_hour": cost_per_hour,
        "expected_downtime_hours": expected_hours,

        # Основное имя поля для Streamlit и summaries
        "estimated_total_impact_eur": estimated_total,

        # Alias, чтобы старый код тоже не ломался
        "estimated_cost_eur": estimated_total,

        "sla_impact": context["sla_impact"],
        "production_impact": get_business_impact_text(risk_level),
        "business_recommendation": get_business_recommendation(risk_level),
    }