import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path(__file__).parent.parent / "data"


def load_carbon_data():
    """Load food carbon footprint database."""
    carbon_file = DATA_DIR / "food_carbon_footprint.csv"
    df = pd.read_csv(carbon_file)
    return df


def load_water_data():
    """Load food water footprint database."""
    water_file = DATA_DIR / "food_water_footprint.csv"
    df = pd.read_csv(water_file)
    return df


def get_food_carbon(food_name, carbon_data, serving_weight_g=100):
    """
    Get carbon footprint for a food based on serving weight.
    Returns kg CO2.
    """
    food_lower = food_name.lower()

    for _, row in carbon_data.iterrows():
        if row["food_keyword"] in food_lower:
            carbon_per_100g = row["carbon_per_100g_kg"]
            return (serving_weight_g / 100) * carbon_per_100g

    return None  # Food not found in database


def daily_carbon(nutrition_df, carbon_data, date):
    """Calculate daily carbon footprint for a specific date."""
    day_data = nutrition_df[nutrition_df["Date"].dt.date == date]

    total_carbon = 0
    foods_found = 0
    foods_missing = []

    for _, row in day_data.iterrows():
        weight = row.get("Serving Weight (g)", 100)
        if pd.isna(weight):
            weight = 100

        carbon = get_food_carbon(row["Food Name"], carbon_data, weight)
        if carbon is not None:
            total_carbon += carbon
            foods_found += 1
        else:
            foods_missing.append(row["Food Name"])

    return {
        "date": date,
        "total_carbon_kg": total_carbon,
        "foods_found": foods_found,
        "foods_missing": foods_missing,
    }


def monthly_carbon(nutrition_df, carbon_data, days=30):
    """Calculate total carbon for past N days."""
    cutoff = datetime.now() - timedelta(days=days)
    recent = nutrition_df[nutrition_df["Date"] >= cutoff]

    nutrition_df_copy = recent.copy()
    nutrition_df_copy["date"] = nutrition_df_copy["Date"].dt.date

    total_carbon = 0
    for date in nutrition_df_copy["date"].unique():
        day = daily_carbon(nutrition_df_copy, carbon_data, date)
        total_carbon += day["total_carbon_kg"]

    return {
        "days": days,
        "total_carbon_kg": total_carbon,
        "average_per_day_kg": total_carbon / days if days > 0 else 0,
    }


def get_food_water(food_name, water_data, serving_weight_g=100):
    """
    Get water footprint for a food based on serving weight.
    Returns liters of water.
    """
    food_lower = food_name.lower()

    for _, row in water_data.iterrows():
        if row["food_keyword"] in food_lower:
            water_per_100g = row["water_per_100g_liters"]
            return (serving_weight_g / 100) * water_per_100g

    return None


def daily_water(nutrition_df, water_data, date):
    """Calculate daily water footprint for a specific date."""
    day_data = nutrition_df[nutrition_df["Date"].dt.date == date]

    total_water = 0
    foods_found = 0

    for _, row in day_data.iterrows():
        weight = row.get("Serving Weight (g)", 100)
        if pd.isna(weight):
            weight = 100

        water = get_food_water(row["Food Name"], water_data, weight)
        if water is not None:
            total_water += water
            foods_found += 1

    return {
        "date": date,
        "total_water_liters": total_water,
        "foods_found": foods_found,
    }


def monthly_water(nutrition_df, water_data, days=30):
    """Calculate total water for past N days."""
    cutoff = datetime.now() - timedelta(days=days)
    recent = nutrition_df[nutrition_df["Date"] >= cutoff]

    nutrition_df_copy = recent.copy()
    nutrition_df_copy["date"] = nutrition_df_copy["Date"].dt.date

    total_water = 0
    for date in nutrition_df_copy["date"].unique():
        day = daily_water(nutrition_df_copy, water_data, date)
        total_water += day["total_water_liters"]

    return {
        "days": days,
        "total_water_liters": total_water,
        "average_per_day_liters": total_water / days if days > 0 else 0,
    }


def carbon_by_food_type(nutrition_df, carbon_data):
    """Break down carbon footprint by major food categories."""
    carbon_data_dict = dict(zip(carbon_data["food_keyword"], carbon_data["carbon_per_100g_kg"]))

    categories = {
        "beef": 0,
        "pork": 0,
        "chicken": 0,
        "fish": 0,
        "dairy": 0,
        "plant_based": 0,
        "other": 0,
    }

    category_keywords = {
        "beef": ["beef"],
        "pork": ["pork"],
        "chicken": ["chicken", "turkey"],
        "fish": ["salmon", "trout", "cod", "tuna", "shrimp"],
        "dairy": ["milk", "cheese", "yogurt", "butter", "eggs"],
        "plant_based": ["tofu", "lentils", "beans", "nuts"],
    }

    for _, row in nutrition_df.iterrows():
        weight = row.get("Serving Weight (g)", 100)
        if pd.isna(weight):
            weight = 100

        food_lower = row["Food Name"].lower()
        carbon = get_food_carbon(row["Food Name"], carbon_data, weight)

        if carbon is None:
            categories["other"] += 0
        else:
            assigned = False
            for category, keywords in category_keywords.items():
                for keyword in keywords:
                    if keyword in food_lower:
                        categories[category] += carbon
                        assigned = True
                        break
                if assigned:
                    break

            if not assigned:
                categories["other"] += carbon

    return categories


def water_by_food_type(nutrition_df, water_data):
    """Break down water footprint by major food categories."""
    categories = {
        "beef": 0,
        "pork": 0,
        "chicken": 0,
        "fish": 0,
        "dairy": 0,
        "plant_based": 0,
        "other": 0,
    }

    category_keywords = {
        "beef": ["beef"],
        "pork": ["pork"],
        "chicken": ["chicken", "turkey"],
        "fish": ["salmon", "trout", "cod", "tuna", "shrimp"],
        "dairy": ["milk", "cheese", "yogurt", "butter", "eggs"],
        "plant_based": ["tofu", "lentils", "beans", "nuts"],
    }

    for _, row in nutrition_df.iterrows():
        weight = row.get("Serving Weight (g)", 100)
        if pd.isna(weight):
            weight = 100

        food_lower = row["Food Name"].lower()
        water = get_food_water(row["Food Name"], water_data, weight)

        if water is None:
            categories["other"] += 0
        else:
            assigned = False
            for category, keywords in category_keywords.items():
                for keyword in keywords:
                    if keyword in food_lower:
                        categories[category] += water
                        assigned = True
                        break
                if assigned:
                    break

            if not assigned:
                categories["other"] += water

    return categories
