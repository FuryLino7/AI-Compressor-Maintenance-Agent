# AI Compressor Maintenance Insight Agent

SAP-style AI-assisted workflow for compressor performance alert processing and maintenance request initiation.

This project is a predictive maintenance prototype for asset-intensive industries. It analyzes compressor sensor data, asset criticality, maintenance history, and production impact to estimate equipment risk, recommend maintenance actions, and generate a draft maintenance notification for human review.

## Demo Scenario

| Asset | Scenario | Risk Level | Estimated Impact |
|---|---|---|---:|
| COMP-01 | Bearing degradation / lubrication issue | Critical | €54,000 |
| COMP-02 | Normal operation | Low | €0 |
| COMP-03 | Air leak / pressure loss | High | €36,000 |
| COMP-04 | Cooling issue / overheating | Medium | €6,000 |

## How to Run

```bash
cd AI-Compressor-Maintenance-Agent

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
python src/data_generator.py
streamlit run app/streamlit_app.py
```

