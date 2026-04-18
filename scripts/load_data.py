import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path(__file__).parent.parent / "data"


def load_nutrition():
    """Load MacroFactor nutrition export."""
    nutrition_file = sorted(DATA_DIR.glob("macrofactor_nutrition/*.csv"))[-1]
    df = pd.read_csv(nutrition_file)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def load_workouts():
    """Load MacroFactor workouts export."""
    workouts_file = sorted(DATA_DIR.glob("macrofactor_workouts/*.csv"))[-1]
    df = pd.read_csv(workouts_file)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def top_foods(nutrition_df, days=7):
    """Most common foods in past N days."""
    cutoff = datetime.now() - timedelta(days=days)
    recent = nutrition_df[nutrition_df["Date"] >= cutoff]
    return recent["Food Name"].value_counts().head(10)


def food_stats(nutrition_df, food_name, days=30):
    """Stats for a specific food: frequency, avg macros, total intake."""
    cutoff = datetime.now() - timedelta(days=days)
    recent = nutrition_df[nutrition_df["Date"] >= cutoff]
    food_entries = recent[recent["Food Name"].str.contains(food_name, case=False, na=False)]

    if food_entries.empty:
        return None

    return {
        "food": food_name,
        "frequency": len(food_entries),
        "avg_calories": food_entries["Calories (kcal)"].mean(),
        "total_calories": food_entries["Calories (kcal)"].sum(),
        "avg_protein": food_entries["Protein (g)"].mean(),
        "avg_carbs": food_entries["Carbs (g)"].mean(),
        "avg_fat": food_entries["Fat (g)"].mean(),
    }


def daily_macros(nutrition_df, date=None):
    """Daily macro totals."""
    if date is None:
        date = datetime.now().date()
    else:
        date = pd.to_datetime(date).date()

    day_data = nutrition_df[nutrition_df["Date"].dt.date == date]

    return {
        "date": date,
        "calories": day_data["Calories (kcal)"].sum(),
        "protein": day_data["Protein (g)"].sum(),
        "carbs": day_data["Carbs (g)"].sum(),
        "fat": day_data["Fat (g)"].sum(),
    }
