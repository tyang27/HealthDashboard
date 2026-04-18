from load_data import load_nutrition
from datetime import datetime, timedelta

MEAT_KEYWORDS = {
    "beef", "chicken", "pork", "lamb", "turkey", "fish", "salmon", "tuna",
    "shrimp", "bacon", "ham", "sausage", "steak", "burger", "meat", "ribs",
    "duck", "wings", "breast", "thigh", "meatball", "anchovies",
    "oyster", "lobster", "crab", "scallop", "clam", "squid", "octopus",
    "prawn", "cod", "halibut", "trout", "mackerel", "sardine", "tilapia", "eel",
}


def is_complete_day(nutrition_df, date, min_calories=1000):
    """Check if a day has sufficient logging (default >= 1000 calories)."""
    day_data = nutrition_df[nutrition_df["Date"].dt.date == date]
    cals = day_data["Calories (kcal)"].sum()
    return cals >= min_calories


def is_vegetarian_day(nutrition_df, date):
    """Check if all foods eaten on a date are vegetarian."""
    day_data = nutrition_df[nutrition_df["Date"].dt.date == date]
    foods = day_data["Food Name"].str.lower()

    for food in foods:
        for keyword in MEAT_KEYWORDS:
            if keyword in food:
                return False
    return True


def vegetarian_days_summary(nutrition_df):
    """Count complete vegetarian days and return summary."""
    nutrition_df = nutrition_df.copy()
    nutrition_df["date"] = nutrition_df["Date"].dt.date

    complete_veggie_days = 0
    total_complete_days = 0

    for date in nutrition_df["date"].unique():
        if is_complete_day(nutrition_df, date):
            total_complete_days += 1
            if is_vegetarian_day(nutrition_df, date):
                complete_veggie_days += 1

    return {
        "vegetarian_days": complete_veggie_days,
        "total_complete_days": total_complete_days,
        "percentage": (complete_veggie_days / total_complete_days * 100) if total_complete_days > 0 else 0,
    }


def vegetarian_days_recent(nutrition_df, days=30):
    """Vegetarian days in the past N days."""
    cutoff = datetime.now() - timedelta(days=days)
    recent = nutrition_df[nutrition_df["Date"] >= cutoff]
    return vegetarian_days_summary(recent)


def top_meats(nutrition_df):
    """Rank meat types by frequency in diet."""
    meat_counts = {keyword: 0 for keyword in MEAT_KEYWORDS}
    foods = nutrition_df["Food Name"].str.lower()

    for food in foods:
        for keyword in MEAT_KEYWORDS:
            if keyword in food:
                meat_counts[keyword] += 1
                break  # Count each food only once

    # Sort by count, filter out zeros
    ranked = sorted(
        [(meat, count) for meat, count in meat_counts.items() if count > 0],
        key=lambda x: x[1],
        reverse=True
    )
    return ranked
