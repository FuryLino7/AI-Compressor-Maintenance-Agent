import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ------------------------------------------------------------
# Path setup
# ------------------------------------------------------------
# Нужно, чтобы Streamlit видел папку src/
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.data_loader import load_all_data
from src.analysis_pipeline import analyze_asset


# ------------------------------------------------------------
# Page config
# ------------------------------------------------------------
st.set_page_config(
    page_title="AI Compressor Maintenance Insight Agent",
    page_icon="🛠️",
    layout="wide"
)


# ------------------------------------------------------------
# Cached data loading
# ------------------------------------------------------------
@st.cache_data
def cached_load_data():
    """
    Загружаем данные один раз и кешируем,
    чтобы Streamlit не перечитывал CSV при каждом клике.
    """
    return load_all_data()


@st.cache_data
def cached_analyze_asset(asset_id: str):
    """
    Кешируем анализ выбранного компрессора.
    """
    return analyze_asset(asset_id)


# ------------------------------------------------------------
# Helper functions for UI
# ------------------------------------------------------------
def format_eur(value):
    try:
        return f"€{value:,.0f}"
    except Exception:
        return "N/A"


def risk_badge(risk_level: str):
    """
    Показывает risk level с визуальным статусом.
    """
    if risk_level == "Critical":
        st.error("Critical Risk")
    elif risk_level == "High":
        st.warning("High Risk")
    elif risk_level == "Medium":
        st.info("Medium Risk")
    else:
        st.success("Low Risk")


def show_list(items):
    """
    Красиво выводит список.
    """
    if not items:
        st.write("No items detected.")
        return

    for item in items:
        st.markdown(f"- {item}")

@st.cache_data
def cached_analyze_all_assets(asset_ids_tuple):
    """
    Анализирует все компрессоры и собирает краткую таблицу для Fleet Overview.
    asset_ids_tuple нужен, потому что Streamlit cache лучше работает с tuple, чем с list.
    """
    rows = []

    for asset_id in asset_ids_tuple:
        result = analyze_asset(asset_id)

        business_impact = result.get("business_impact", {})

        rows.append(
            {
                "Asset ID": result.get("asset_id"),
                "Asset Name": result.get("asset_name"),
                "Location": result.get("location"),
                "Criticality": result.get("criticality"),
                "Risk Level": result.get("risk_level"),
                "Risk Score": result.get("risk_score"),
                "ML Anomaly": "Yes" if result.get("ml_anomaly_detected") else "No",
                "Primary Scenario": result.get("primary_scenario"),
                "Estimated Impact": business_impact.get(
                    "estimated_total_impact_eur",
                    business_impact.get("estimated_cost_eur", 0)
                ),
                "Recommended Action": (
                    result.get("recommended_actions", ["N/A"])[0]
                    if result.get("recommended_actions")
                    else "N/A"
                ),
            }
        )

    fleet_df = pd.DataFrame(rows)

    risk_order = {
        "Critical": 0,
        "High": 1,
        "Medium": 2,
        "Low": 3,
    }

    fleet_df["Risk Sort"] = fleet_df["Risk Level"].map(risk_order).fillna(99)
    fleet_df = fleet_df.sort_values(
        by=["Risk Sort", "Risk Score"],
        ascending=[True, False]
    ).drop(columns=["Risk Sort"])

    return fleet_df


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------
st.title("AI Compressor Maintenance Insight Agent")
st.caption(
    "SAP-style AI-assisted workflow for compressor performance alert processing "
    "and maintenance request initiation."
)


# ------------------------------------------------------------
# Load data
# ------------------------------------------------------------
try:
    data = cached_load_data()
    asset_master_df = data["asset_master"]
    sensor_df = data["sensor_readings"]
    maintenance_history_df = data["maintenance_history"]
    production_impact_df = data["production_impact"]
except Exception as e:
    st.error("Failed to load data. Please check CSV files in the data/ folder.")
    st.exception(e)
    st.stop()


# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------
st.sidebar.header("Analysis Controls")

asset_ids = asset_master_df["asset_id"].unique().tolist()

selected_asset_id = st.sidebar.selectbox(
    "Select compressor asset",
    asset_ids,
    index=0
)

st.sidebar.markdown("---")

run_analysis = st.sidebar.button("Analyze Asset Alert", type="primary")

st.sidebar.markdown("---")
st.sidebar.caption("Demo data source: synthetic compressor dataset")


# ------------------------------------------------------------
# Default behavior
# ------------------------------------------------------------
if not run_analysis:
    st.info("Select a compressor asset in the sidebar and click **Analyze Asset Alert**.")
    st.stop()


# ------------------------------------------------------------
# Run analysis
# ------------------------------------------------------------
try:
    analysis = cached_analyze_asset(selected_asset_id)
except Exception as e:
    st.error("Asset analysis failed.")
    st.exception(e)
    st.stop()


# ------------------------------------------------------------
# Prepare selected asset sensor data
# ------------------------------------------------------------
selected_sensor_df = sensor_df[sensor_df["asset_id"] == selected_asset_id].copy()

if selected_sensor_df.empty:
    st.error(f"No sensor data found for asset {selected_asset_id}")
    st.stop()

selected_sensor_df["timestamp"] = pd.to_datetime(selected_sensor_df["timestamp"])
selected_sensor_df = selected_sensor_df.sort_values("timestamp")


# ------------------------------------------------------------
# Top summary metrics
# ------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Asset", analysis.get("asset_id", "N/A"))

with col2:
    st.metric("Risk Score", analysis.get("risk_score", "N/A"))

with col3:
    st.metric("Risk Level", analysis.get("risk_level", "N/A"))

with col4:
    impact = analysis.get("business_impact", {}).get("estimated_total_impact_eur", 0)
    st.metric("Estimated Impact", format_eur(impact))


st.markdown("---")


# ------------------------------------------------------------
# Tabs
# ------------------------------------------------------------
fleet_tab, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "Fleet Overview",
        "Asset Overview",
        "Sensor Dashboard",
        "Risk Qualification",
        "Recommendations",
        "AI Summaries",
        "Maintenance Notification",
    ]
)


with fleet_tab:
    st.subheader("Fleet Overview")

    st.caption(
        "Overview of all compressor assets ranked by risk level, business impact, "
        "and recommended maintenance action."
    )

    fleet_df = cached_analyze_all_assets(tuple(asset_ids))

    # Верхние KPI
    total_assets = len(fleet_df)
    critical_count = (fleet_df["Risk Level"] == "Critical").sum()
    high_count = (fleet_df["Risk Level"] == "High").sum()
    total_estimated_impact = fleet_df["Estimated Impact"].sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Assets", total_assets)

    with col2:
        st.metric("Critical Assets", critical_count)

    with col3:
        st.metric("High Risk Assets", high_count)

    with col4:
        st.metric("Total Estimated Impact", format_eur(total_estimated_impact))

    st.markdown("### Asset Risk Ranking")

    # Фильтр по risk level
    selected_risk_levels = st.multiselect(
        "Filter by risk level",
        ["Critical", "High", "Medium", "Low"],
        default=["Critical", "High", "Medium", "Low"],
    )

    filtered_fleet_df = fleet_df[
        fleet_df["Risk Level"].isin(selected_risk_levels)
    ].copy()

    # Форматируем деньги отдельной колонкой, чтобы не ломать числовой расчет
    filtered_fleet_df["Estimated Impact Display"] = filtered_fleet_df[
        "Estimated Impact"
    ].apply(format_eur)

    display_df = filtered_fleet_df[
        [
            "Asset ID",
            "Asset Name",
            "Location",
            "Criticality",
            "Risk Level",
            "Risk Score",
            "ML Anomaly",
            "Primary Scenario",
            "Estimated Impact Display",
            "Recommended Action",
        ]
    ].rename(
        columns={
            "Estimated Impact Display": "Estimated Impact"
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Recommended Focus")

    if critical_count > 0:
        st.error(
            "At least one compressor has a Critical risk level. "
            "Immediate maintenance review is recommended."
        )
    elif high_count > 0:
        st.warning(
            "High-risk compressor assets detected. "
            "Maintenance should be scheduled as soon as possible."
        )
    else:
        st.success(
            "No high or critical compressor risks detected. "
            "Continue regular monitoring."
        )

# ------------------------------------------------------------
# Tab 1: Asset Overview
# ------------------------------------------------------------
with tab1:
    st.subheader("Asset Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Asset ID", analysis.get("asset_id", "N/A"))
        st.metric("Asset Type", analysis.get("asset_type", "N/A"))

    with col2:
        st.metric("Plant", analysis.get("plant", "N/A"))
        st.metric("Location", analysis.get("location", "N/A"))

    with col3:
        st.metric("Criticality", analysis.get("criticality", "N/A"))
        st.metric(
            "Downtime Cost / Hour",
            format_eur(analysis.get("downtime_cost_eur_per_hour", 0))
        )

    st.markdown("### Connected Business Process")
    st.write(analysis.get("connected_process", "N/A"))

    st.markdown("### Recent Maintenance History")

    asset_maintenance = maintenance_history_df[
        maintenance_history_df["asset_id"] == selected_asset_id
    ].copy()

    if asset_maintenance.empty:
        st.info("No maintenance history found for this asset.")
    else:
        st.dataframe(asset_maintenance, use_container_width=True)


# ------------------------------------------------------------
# Tab 2: Sensor Dashboard
# ------------------------------------------------------------
with tab2:
    st.subheader("Sensor Dashboard")

    st.caption(
        "Sensor trends for the selected compressor asset. "
        "The dashboard highlights operational patterns used for risk qualification."
    )

    latest_row = selected_sensor_df.iloc[-1]
    first_row = selected_sensor_df.iloc[0]

    def delta_percent(first_value, latest_value):
        if first_value == 0:
            return 0
        return ((latest_value - first_value) / first_value) * 100

    # KPI cards по последним значениям
    st.markdown("### Latest Sensor Readings")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        vibration_delta = delta_percent(
            first_row["vibration_mm_s"],
            latest_row["vibration_mm_s"]
        )
        st.metric(
            "Vibration",
            f"{latest_row['vibration_mm_s']:.2f} mm/s",
            f"{vibration_delta:.1f}%"
        )

    with col2:
        oil_delta = delta_percent(
            first_row["oil_temperature_c"],
            latest_row["oil_temperature_c"]
        )
        st.metric(
            "Oil Temperature",
            f"{latest_row['oil_temperature_c']:.1f} °C",
            f"{oil_delta:.1f}%"
        )

    with col3:
        motor_delta = delta_percent(
            first_row["motor_temperature_c"],
            latest_row["motor_temperature_c"]
        )
        st.metric(
            "Motor Temperature",
            f"{latest_row['motor_temperature_c']:.1f} °C",
            f"{motor_delta:.1f}%"
        )

    with col4:
        efficiency_delta = latest_row["efficiency_percent"] - first_row["efficiency_percent"]
        st.metric(
            "Efficiency",
            f"{latest_row['efficiency_percent']:.1f}%",
            f"{efficiency_delta:.1f} pp"
        )

    st.markdown("---")

    # Функция для графика одной метрики
    def show_metric_chart(metric_name: str, title: str):
        chart_df = selected_sensor_df[["timestamp", metric_name]].copy()
        chart_df = chart_df.set_index("timestamp")

        st.markdown(f"#### {title}")
        st.line_chart(chart_df, height=220)

    # Графики в две колонки
    left_col, right_col = st.columns(2)

    with left_col:
        show_metric_chart("vibration_mm_s", "Vibration Trend, mm/s")
        show_metric_chart("oil_temperature_c", "Oil Temperature Trend, °C")
        show_metric_chart("discharge_pressure_bar", "Discharge Pressure Trend, bar")
        show_metric_chart("power_consumption_kw", "Power Consumption Trend, kW")

    with right_col:
        show_metric_chart("motor_temperature_c", "Motor Temperature Trend, °C")
        show_metric_chart("efficiency_percent", "Efficiency Trend, %")
        show_metric_chart("air_flow_m3_min", "Air Flow Trend, m³/min")
        show_metric_chart("load_percent", "Load Trend, %")

    st.markdown("---")

    st.markdown("### Raw Sensor Data Preview")

    st.dataframe(
        selected_sensor_df.tail(20),
        use_container_width=True,
        hide_index=True,
    )

# ------------------------------------------------------------
# Tab 3: Risk Qualification
# ------------------------------------------------------------
with tab3:
    st.subheader("Risk Qualification")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Risk Score", analysis.get("risk_score", "N/A"))

    with col2:
        st.metric("Risk Level", analysis.get("risk_level", "N/A"))

    with col3:
        anomaly_detected = analysis.get("ml_anomaly_detected", False)
        st.metric("ML Anomaly", "Yes" if anomaly_detected else "No")

    st.markdown("### Risk Status")
    risk_badge(analysis.get("risk_level", "Low"))

    st.markdown("### Risk Factors")
    show_list(analysis.get("risk_factors", []))

    st.markdown("### Business Impact")

    business_impact = analysis.get("business_impact", {})

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Expected Downtime",
            f"{business_impact.get('expected_downtime_hours', 0)} h"
        )

    with col2:
        st.metric(
            "Estimated Impact",
            format_eur(business_impact.get("estimated_total_impact_eur", 0))
        )

    with col3:
        st.metric(
            "SLA Impact",
            business_impact.get("sla_impact", "N/A")
        )


# ------------------------------------------------------------
# Tab 4: Recommendations
# ------------------------------------------------------------
with tab4:
    st.subheader("Root Cause Hypothesis & Recommendations")

    st.caption(
        "The agent converts sensor patterns and risk factors into a primary diagnostic "
        "scenario, possible causes, and recommended maintenance actions."
    )

    primary_scenario = analysis.get(
        "primary_scenario",
        "No primary scenario detected"
    )

    suggested_timeframe = analysis.get(
        "suggested_timeframe",
        "No timeframe suggested"
    )

    risk_level = analysis.get("risk_level", "Low")

    # Primary scenario card
    st.markdown("### Primary Scenario")

    if risk_level in ["Critical", "High"]:
        st.warning(primary_scenario)
    elif risk_level == "Medium":
        st.info(primary_scenario)
    else:
        st.success(primary_scenario)

    st.markdown("### Suggested Timeframe")
    st.write(suggested_timeframe)

    st.markdown("---")

    # Causes and actions
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Possible Causes")
        possible_causes = analysis.get("possible_causes", [])

        if possible_causes:
            for cause in possible_causes:
                st.markdown(f"- {cause}")
        else:
            st.write("No possible causes detected.")

    with col2:
        st.markdown("### Recommended Actions")
        recommended_actions = analysis.get("recommended_actions", [])

        if recommended_actions:
            for index, action in enumerate(recommended_actions, start=1):
                st.markdown(f"{index}. {action}")
        else:
            st.write("No recommended actions generated.")

    st.markdown("---")

    # Diagnostic signals
    st.markdown("### Diagnostic Signals")

    diagnostic_signals = analysis.get("diagnostic_signals", {})

    if diagnostic_signals:
        diagnostic_df = pd.DataFrame(
            [
                {"Signal": key, "Value": value}
                for key, value in diagnostic_signals.items()
            ]
        )

        st.dataframe(
            diagnostic_df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No diagnostic signals available.")

    st.markdown("### Maintenance Decision Note")

    st.info(
        "The root cause analysis provides hypotheses based on sensor patterns. "
        "Physical inspection is required before maintenance decisions are finalized."
    )

# ------------------------------------------------------------
# Tab 5: AI Summaries
# ------------------------------------------------------------
with tab5:
    st.subheader("AI-generated Role-based Summaries")

    st.caption(
        "The same asset alert is explained differently for engineering and management users."
    )

    engineer_summary = analysis.get(
        "engineer_summary",
        "No engineer summary generated."
    )

    manager_summary = analysis.get(
        "manager_summary",
        "No manager summary generated."
    )

    summary_tab1, summary_tab2 = st.tabs(
        [
            "Engineer View",
            "Manager View",
        ]
    )

    with summary_tab1:
        st.markdown("### Engineer Summary")
        st.write(engineer_summary)

        st.markdown("### Engineering Context")

        engineering_context = {
            "Asset ID": analysis.get("asset_id"),
            "Risk Level": analysis.get("risk_level"),
            "Primary Scenario": analysis.get("primary_scenario"),
            "ML Anomaly Detected": "Yes" if analysis.get("ml_anomaly_detected") else "No",
            "Anomaly Score": analysis.get("anomaly_score"),
            "Suggested Timeframe": analysis.get("suggested_timeframe"),
        }

        engineering_context_df = pd.DataFrame(
            [
                {"Field": key, "Value": value}
                for key, value in engineering_context.items()
            ]
        )

        st.dataframe(
            engineering_context_df,
            use_container_width=True,
            hide_index=True,
        )

    with summary_tab2:
        st.markdown("### Manager Summary")
        st.write(manager_summary)

        st.markdown("### Business Context")

        business_impact = analysis.get("business_impact", {})

        business_context = {
            "Asset ID": analysis.get("asset_id"),
            "Location": analysis.get("location"),
            "Connected Process": analysis.get("connected_process"),
            "Risk Level": analysis.get("risk_level"),
            "Estimated Impact": format_eur(
                business_impact.get(
                    "estimated_total_impact_eur",
                    business_impact.get("estimated_cost_eur", 0)
                )
            ),
            "SLA Impact": business_impact.get("sla_impact"),
            "Business Recommendation": business_impact.get("business_recommendation"),
        }

        business_context_df = pd.DataFrame(
            [
                {"Field": key, "Value": value}
                for key, value in business_context.items()
            ]
        )

        st.dataframe(
            business_context_df,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")

    # Download summaries
    summary_text = f"""
AI Compressor Maintenance Insight Agent

Asset: {analysis.get("asset_id")}
Risk Level: {analysis.get("risk_level")}
Primary Scenario: {analysis.get("primary_scenario")}

Engineer Summary:
{engineer_summary}

Manager Summary:
{manager_summary}
"""

    st.download_button(
        label="Download summaries as TXT",
        data=summary_text,
        file_name=f"{analysis.get('asset_id')}_summaries.txt",
        mime="text/plain",
    )

# ------------------------------------------------------------
# Tab 6: Maintenance Notification
# ------------------------------------------------------------
with tab6:
    st.subheader("Draft Maintenance Notification")

    notification = analysis.get("maintenance_notification", {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Notification Details")
        st.write(f"**Type:** {notification.get('notification_type', 'N/A')}")
        st.write(f"**Asset:** {notification.get('asset_id', selected_asset_id)}")
        st.write(f"**Priority:** {notification.get('priority', 'N/A')}")
        st.write(
            f"**Approval required:** "
            f"{'Yes' if notification.get('approval_required', True) else 'No'}"
        )

    with col2:
        st.markdown("### Short Description")
        st.write(notification.get("short_description", "N/A"))

    st.markdown("### Problem Description")
    st.write(notification.get("problem_description", "N/A"))

    st.markdown("### Recommended Action")
    st.write(notification.get("recommended_action", "N/A"))

    st.markdown("### Business Impact")
    st.write(notification.get("business_impact", "N/A"))

    st.markdown("---")
    st.markdown("### Human Review")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Approve notification"):
            st.success("Maintenance notification approved by maintenance planner.")

    with col2:
        if st.button("Request additional analysis"):
            st.info("Additional analysis requested. The notification remains in review.")

    with col3:
        if st.button("Escalate to manager"):
            st.warning("Notification escalated to maintenance manager.")