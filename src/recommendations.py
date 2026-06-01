def generate_root_cause_and_recommendations(
    latest_data: dict,
    trends: dict,
    risk_factors: list,
) -> dict:
    vibration = latest_data.get("vibration_mm_s", 0)
    oil_temp = latest_data.get("oil_temperature_c", 0)
    motor_temp = latest_data.get("motor_temperature_c", 0)
    pressure = latest_data.get("discharge_pressure_bar", 10)
    efficiency = latest_data.get("efficiency_percent", 100)
    load = latest_data.get("load_percent", 0)

    power_trend = trends.get("power_consumption_change_percent", 0)
    efficiency_change = trends.get("efficiency_change_points", 0)
    pressure_change = trends.get("pressure_change_percent", 0)

    bearing_pattern = (
        vibration > 4.5
        and oil_temp > 80
        and efficiency < 86
    )

    pressure_loss_pattern = (
        pressure < 7.5
        and efficiency < 86
    ) or (
        "Low discharge pressure" in risk_factors
        or "Very low discharge pressure" in risk_factors
    )

    cooling_pattern = (
        motor_temp > 85
        and oil_temp > 80
        and load > 85
        and vibration <= 4.5
    )

    energy_efficiency_pattern = (
        power_trend > 8
        and efficiency_change < -5
    )

    if bearing_pattern:
        primary_scenario = "Bearing degradation / lubrication issue"
        possible_causes = [
            "Bearing wear",
            "Lubrication degradation",
            "Mechanical imbalance",
        ]
        recommended_actions = [
            "Inspect bearing condition",
            "Check lubrication system",
            "Review recent vibration trend",
            "Schedule inspection within 24–48 hours",
        ]
        suggested_timeframe = "Within 24–48 hours"

    elif pressure_loss_pattern:
        primary_scenario = "Air leak / pressure loss"
        possible_causes = [
            "Compressed air leakage",
            "Valve issue",
            "Clogged filter",
            "Pressure control problem",
        ]
        recommended_actions = [
            "Inspect air distribution line",
            "Check valves and filters",
            "Verify pressure control system",
            "Compare discharge pressure trend with air flow demand",
        ]
        suggested_timeframe = "Within 48 hours"

    elif cooling_pattern:
        primary_scenario = "Cooling issue / overheating"
        possible_causes = [
            "Cooling system degradation",
            "Blocked heat exchanger",
            "Overload operation",
        ]
        recommended_actions = [
            "Inspect cooling system",
            "Clean heat exchanger",
            "Reduce compressor load if temperature continues rising",
        ]
        suggested_timeframe = "Within 24–48 hours"

    elif energy_efficiency_pattern:
        primary_scenario = "Energy efficiency degradation"
        possible_causes = [
            "Energy performance degradation",
            "Worn components",
            "Suboptimal operating mode",
        ]
        recommended_actions = [
            "Compare performance with compressor efficiency baseline",
            "Schedule performance inspection",
            "Review operating parameters",
        ]
        suggested_timeframe = "Within 3–5 days"

    else:
        primary_scenario = "No clear root cause pattern detected"
        possible_causes = [
            "No clear root cause pattern detected"
        ]
        recommended_actions = [
            "Continue monitoring and follow regular maintenance plan"
        ]
        suggested_timeframe = "Continue regular monitoring"

    return {
        "primary_scenario": primary_scenario,
        "possible_causes": possible_causes,
        "recommended_actions": recommended_actions,
        "suggested_timeframe": suggested_timeframe,
        "diagnostic_signals": {
            "vibration_mm_s": vibration,
            "oil_temperature_c": oil_temp,
            "motor_temperature_c": motor_temp,
            "discharge_pressure_bar": pressure,
            "efficiency_percent": efficiency,
            "load_percent": load,
            "power_consumption_change_percent": power_trend,
            "efficiency_change_points": efficiency_change,
            "pressure_change_percent": pressure_change,
        },
    }