def get_estimated_impact(analysis_result: dict) -> float:
    """
    Достает impact из разных возможных ключей.
    Это защищает от ошибок, если структура business_impact немного менялась.
    """
    business_impact = analysis_result.get("business_impact", {})

    return (
        business_impact.get("estimated_total_impact_eur")
        or business_impact.get("estimated_cost_eur")
        or 0
    )


def generate_engineer_summary(analysis_result: dict) -> str:
    asset_id = analysis_result["asset_id"]
    risk_level = analysis_result["risk_level"]
    possible_causes = analysis_result.get("possible_causes", [])
    recommended_actions = analysis_result.get("recommended_actions", [])

    cause_text = ", ".join(possible_causes[:3]) if possible_causes else "an unclear technical issue"

    action_text = (
        recommended_actions[0]
        if recommended_actions
        else "continue monitoring"
    )

    return (
        f"{asset_id} shows a {risk_level.lower()} risk condition based on the latest "
        f"compressor sensor patterns. The detected pattern may indicate {cause_text}. "
        f"The recommended next step is to {action_text.lower()}. "
        f"This analysis is based on sensor trends and should be verified through "
        f"physical inspection before maintenance decisions are finalized."
    )


def generate_manager_summary(analysis_result: dict) -> str:
    asset_id = analysis_result["asset_id"]
    location = analysis_result.get("location", "unknown location")
    connected_process = analysis_result.get("connected_process", "unknown process")
    risk_level = analysis_result["risk_level"]

    estimated_impact = get_estimated_impact(analysis_result)

    recommended_actions = analysis_result.get("recommended_actions", [])
    action_text = (
        recommended_actions[0]
        if recommended_actions
        else "continue monitoring"
    )

    return (
        f"{asset_id} at {location} has a {risk_level.lower()} risk of operational disruption "
        f"for {connected_process}. If no action is taken, the estimated business impact "
        f"may reach €{estimated_impact:,.0f}. The recommended next step is to "
        f"{action_text.lower()}."
    )