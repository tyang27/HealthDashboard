# HealthDashboard

Personal health and fitness analytics dashboard integrating MacroFactor nutrition tracking and Withings biometric data.

## Structure

- **data/** — Raw exported data from MacroFactor and Withings
  - macrofactor_nutrition/ — Nutrition logs
  - macrofactor_workouts/ — Workout data
  - withings/ — Sleep, activity, weight measurements
- **analyses/** — Jupyter notebooks for exploratory analysis
- **scripts/** — Reusable Python scripts for data parsing and ETL
- **webapp/** — Web application for insights and LLM-powered queries

## Getting Started

Place raw data exports in the `data/` folders. Run scripts to parse and normalize, then use notebooks for analysis.
