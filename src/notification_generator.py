def generate_maintenance_notification(
    asset_context: dict,
    risk_result: dict,
    recommendations: dict,
    business_impact: dict,
) -> dict:
    asset_id = asset_context["asset_id"]
    asset_name = asset_context["asset_name"]
    priority = risk_result["risk_level"]

    possible_causes = recommendations.get("possible_causes", [])
    recommended_actions = recommendations.get("recommended_actions", [])

    primary_cause = possible_causes[0] if possible_causes else "Unknown issue"
    primary_action = (
        recommended_actions[0]
        if recommended_actions
        else "Review asset condition"
    )

    estimated_impact = business_impact.get("estimated_total_impact_eur", 0)

    short_description = f"{primary_cause} suspected for {asset_id}"

    problem_description = (
        f"{asset_id} ({asset_name}) shows abnormal operating patterns. "
        f"The current risk level is {priority}. "
        f"The analysis suggests a possible issue related to {primary_cause.lower()}."
    )

    business_impact_text = (
        f"Potential downtime impact estimated at €{estimated_impact:,.0f}."
    )

    approval_required = priority in ["High", "Critical"]

    return {
        "notification_type": "Maintenance Request",
        "asset_id": asset_id,
        "asset_name": asset_name,
        "priority": priority,
        "short_description": short_description,
        "problem_description": problem_description,
        "recommended_action": primary_action,
        "business_impact": business_impact_text,
        "approval_required": approval_required,
    }