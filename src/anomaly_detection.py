import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


FEATURES = [
    "discharge_pressure_bar",
    "air_flow_m3_min",
    "motor_temperature_c",
    "vibration_mm_s",
    "oil_temperature_c",
    "power_consumption_kw",
    "load_percent",
    "efficiency_percent",
]


def detect_asset_anomalies(sensor_df: pd.DataFrame, asset_id: str) -> dict:
    """
    Простая ML anomaly detection.
    Модель обучается на всех sensor readings и оценивает последнюю запись выбранного asset.
    """

    df = sensor_df.copy()

    missing_features = [col for col in FEATURES if col not in df.columns]

    if missing_features:
        raise ValueError(f"Missing features for anomaly detection: {missing_features}")

    feature_df = df[FEATURES].dropna()

    if len(feature_df) < 10:
        return {
            "ml_anomaly_detected": False,
            "anomaly_score": 0.0,
        }

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(feature_df)

    model = IsolationForest(
        contamination=0.12,
        random_state=42
    )

    model.fit(scaled_features)

    asset_df = df[df["asset_id"] == asset_id].copy()

    if asset_df.empty:
        return {
            "ml_anomaly_detected": False,
            "anomaly_score": 0.0,
        }

    latest_asset_row = asset_df.sort_values("timestamp").iloc[-1]
    latest_features = latest_asset_row[FEATURES].to_frame().T

    latest_scaled = scaler.transform(latest_features)

    prediction = model.predict(latest_scaled)[0]
    anomaly_score = model.decision_function(latest_scaled)[0]

    return {
        "ml_anomaly_detected": prediction == -1,
        "anomaly_score": float(anomaly_score),
    }