from src.data_loader import load_all_data
from src.trend_analysis import calculate_metric_trends
from src.risk_scoring import calculate_risk_score
from src.anomaly_detection import detect_asset_anomalies
from src.business_impact import estimate_business_impact
from src.recommendations import generate_root_cause_and_recommendations
from src.notification_generator import generate_maintenance_notification
from src.llm_summary import generate_engineer_summary, generate_manager_summary


def analyze_asset(asset_id: str) -> dict:
    """
    Главная функция анализа.
    Streamlit вызывает именно ее.
    """

    data = load_all_data()

    asset_master_df = data["asset_master"]
    sensor_df = data["sensor_readings"]
    maintenance_history_df = data["maintenance_history"]
    production_impact_df = data["production_impact"]

    asset_row = asset_master_df[asset_master_df["asset_id"] == asset_id]

    if asset_row.empty:
        raise ValueError(f"Asset {asset_id} not found in asset_master.csv")

    asset_context = asset_row.iloc[0].to_dict()

    production_row = production_impact_df[
        production_impact_df["asset_id"] == asset_id
    ]

    if production_row.empty:
        raise ValueError(f"Asset {asset_id} not found in production_impact.csv")

    production_context = production_row.iloc[0].to_dict()

    asset_sensor_df = sensor_df[sensor_df["asset_id"] == asset_id].copy()

    if asset_sensor_df.empty:
        raise ValueError(f"No sensor readings found for asset {asset_id}")

    asset_sensor_df = asset_sensor_df.sort_values("timestamp")
    latest_data = asset_sensor_df.iloc[-1].to_dict()

    asset_maintenance_history = maintenance_history_df[
        maintenance_history_df["asset_id"] == asset_id
    ].copy()

    trends = calculate_metric_trends(asset_sensor_df)

    risk_result = calculate_risk_score(
        latest_data=latest_data,
        trends=trends,
        asset_context=asset_context,
        production_context=production_context,
        maintenance_history=asset_maintenance_history,
    )

    anomaly_result = detect_asset_anomalies(sensor_df, asset_id)

    business_impact = estimate_business_impact(
        asset_id=asset_id,
        risk_level=risk_result["risk_level"],
        production_impact_df=production_impact_df,
    )

    recommendation_result = generate_root_cause_and_recommendations(
        latest_data=latest_data,
        trends=trends,
        risk_factors=risk_result["risk_factors"],
    )

    analysis_result = {
        "asset_id": asset_context["asset_id"],
        "asset_name": asset_context["asset_name"],
        "asset_type": asset_context["asset_type"],
        "plant": asset_context["plant"],
        "location": asset_context["location"],
        "criticality": asset_context["criticality"],
        "manufacturer": asset_context["manufacturer"],
        "installation_year": asset_context["installation_year"],
        "connected_process": production_context["connected_process"],
        "downtime_cost_eur_per_hour": production_context[
            "estimated_downtime_cost_eur_per_hour"
        ],

        "risk_score": risk_result["risk_score"],
        "risk_level": risk_result["risk_level"],
        "risk_factors": risk_result["risk_factors"],

        "ml_anomaly_detected": anomaly_result["ml_anomaly_detected"],
        "anomaly_score": anomaly_result["anomaly_score"],

        "business_impact": business_impact,

        "possible_causes": recommendation_result["possible_causes"],
        "recommended_actions": recommendation_result["recommended_actions"],
        "suggested_timeframe": recommendation_result["suggested_timeframe"],
        "primary_scenario": recommendation_result.get("primary_scenario"),
        "suggested_timeframe": recommendation_result.get("suggested_timeframe"),
        "diagnostic_signals": recommendation_result.get("diagnostic_signals", {}),
    }

    notification = generate_maintenance_notification(
        asset_context=asset_context,
        risk_result=risk_result,
        recommendations=recommendation_result,
        business_impact=business_impact,
    )

    analysis_result["maintenance_notification"] = notification

    analysis_result["engineer_summary"] = generate_engineer_summary(analysis_result)
    analysis_result["manager_summary"] = generate_manager_summary(analysis_result)

    return analysis_result