from src.analysis_pipeline import analyze_asset

assets = ["COMP-01", "COMP-02", "COMP-03", "COMP-04"]

for asset_id in assets:
    print("=" * 80)
    print(f"ASSET: {asset_id}")

    result = analyze_asset(asset_id)

    print("Risk level:", result.get("risk_level"))
    print("Risk score:", result.get("risk_score"))
    print("ML anomaly:", result.get("ml_anomaly_detected"))
    print("Anomaly score:", result.get("anomaly_score"))
    print("Primary scenario:", result.get("primary_scenario"))

    print("\nRisk factors:")
    for item in result.get("risk_factors", []):
        print("-", item)

    print("\nPossible causes:")
    for item in result.get("possible_causes", []):
        print("-", item)

    print("\nRecommended actions:")
    for item in result.get("recommended_actions", []):
        print("-", item)

    print("\nBusiness impact:")
    print(result.get("business_impact"))

    print("\nManager summary:")
    print(result.get("manager_summary"))

    print()

