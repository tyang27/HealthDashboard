import pandas as pd
from datetime import datetime, timedelta
from collections import Counter


def get_frequency(nutrition_df, food_name, days=30):
    """Get frequency of a food in past N days."""
    cutoff = datetime.now() - timedelta(days=days)
    recent = nutrition_df[nutrition_df["Date"] >= cutoff]

    foods = recent["Food Name"].str.lower()
    count = sum(1 for food in foods if food_name.lower() in food)

    return count, days


def estimate_quantity_needed(nutrition_df, food_name, days=30):
    """Estimate how much of a food is consumed in N days."""
    cutoff = datetime.now() - timedelta(days=days)
    recent = nutrition_df[nutrition_df["Date"] >= cutoff]

    food_entries = recent[recent["Food Name"].str.contains(food_name, case=False, na=False)]

    if food_entries.empty:
        return None

    total_weight = food_entries["Serving Weight (g)"].sum()

    return {
        "food": food_name,
        "days": days,
        "total_weight_g": total_weight,
        "average_serving_g": food_entries["Serving Weight (g)"].mean(),
        "frequency": len(food_entries),
        "per_day_g": total_weight / days,
    }


def top_groceries(nutrition_df, top_n=20, days=30):
    """Get top N ingredients to buy with estimated quantities."""
    cutoff = datetime.now() - timedelta(days=days)
    recent = nutrition_df[nutrition_df["Date"] >= cutoff]

    # Count frequency of each food
    food_counts = Counter(recent["Food Name"].str.lower())

    groceries = []
    for food, count in food_counts.most_common(top_n):
        original_food = recent[recent["Food Name"].str.lower() == food]["Food Name"].iloc[0]

        # Get weight data
        food_entries = recent[recent["Food Name"].str.lower() == food]
        total_weight = food_entries["Serving Weight (g)"].sum()
        avg_serving = food_entries["Serving Weight (g)"].mean()

        groceries.append({
            "food": original_food,
            "frequency": count,
            "total_weight_g": total_weight,
            "avg_serving_g": avg_serving,
            "per_day_g": total_weight / days,
        })

    return groceries


def purchase_recommendations(nutrition_df, days=30):
    """
    Generate purchase recommendations based on consumption patterns.

    Returns dict with weekly, bi-weekly, and monthly purchase suggestions.
    """
    groceries = top_groceries(nutrition_df, top_n=30, days=days)

    weekly = []
    biweekly = []
    monthly = []

    for item in groceries:
        per_week_g = item["per_day_g"] * 7
        per_month_g = item["per_day_g"] * 30

        # Estimate shelf life and recommend purchase frequency
        # Perishables (milk, eggs, etc): weekly
        # Semi-perishables (produce): bi-weekly
        # Non-perishables: monthly

        food_lower = item["food"].lower()

        if any(x in food_lower for x in ["milk", "yogurt", "eggs", "meat", "fish", "chicken", "beef", "cheese"]):
            # Perishable - buy weekly
            weekly.append({
                "item": item["food"],
                "frequency": item["frequency"],
                "amount_to_buy": max(per_week_g, 100),  # At least 100g
                "unit": "grams",
            })
        elif any(x in food_lower for x in ["bread", "banana", "apple", "orange", "vegetable", "carrot", "broccoli"]):
            # Semi-perishable - buy bi-weekly
            biweekly.append({
                "item": item["food"],
                "frequency": item["frequency"],
                "amount_to_buy": per_month_g / 2,
                "unit": "grams",
            })
        else:
            # Non-perishable - buy monthly
            monthly.append({
                "item": item["food"],
                "frequency": item["frequency"],
                "amount_to_buy": per_month_g,
                "unit": "grams",
            })

    return {
        "weekly": sorted(weekly, key=lambda x: x["frequency"], reverse=True)[:10],
        "biweekly": sorted(biweekly, key=lambda x: x["frequency"], reverse=True)[:10],
        "monthly": sorted(monthly, key=lambda x: x["frequency"], reverse=True)[:10],
    }


def shopping_estimate(recommendations):
    """Estimate shopping list sizes."""
    return {
        "weekly_items": len(recommendations["weekly"]),
        "biweekly_items": len(recommendations["biweekly"]),
        "monthly_items": len(recommendations["monthly"]),
        "total_items": len(recommendations["weekly"]) + len(recommendations["biweekly"]) + len(recommendations["monthly"]),
    }


def categorize_by_section(recommendations):
    """
    Organize shopping items by grocery store section.

    Returns dict with sections as keys and lists of items as values.
    """
    section_map = {
        "Produce": ["apple", "banana", "orange", "berry", "vegetable", "carrot", "broccoli", "lettuce", "spinach", "kale", "tomato", "cucumber", "pepper", "onion", "garlic", "squash", "zucchini", "potato", "sweet potato"],
        "Dairy": ["milk", "cheese", "yogurt", "butter", "cream"],
        "Meat & Seafood": ["chicken", "beef", "pork", "fish", "salmon", "tuna", "shrimp", "lobster", "crab", "turkey", "duck", "lamb", "sausage", "bacon", "ham", "steak", "burger", "meat", "trout", "cod", "halibut", "tilapia", "eel", "sardine", "mackerel", "oyster", "squid", "octopus", "scallop", "clam"],
        "Eggs": ["egg"],
        "Grains & Bread": ["bread", "cereal", "oat", "rice", "pasta", "flour", "grain"],
        "Pantry & Dry Goods": ["nut", "peanut butter", "olive oil", "oil", "bean", "lentil", "chickpea", "spice", "salt", "sugar", "honey", "jam"],
        "Beverages": ["milk", "coffee", "tea", "juice", "water", "smoothie", "huel", "protein", "electrolyte"],
        "Frozen": ["frozen"],
    }

    sections = {section: [] for section in section_map.keys()}

    # Combine all items from all frequencies
    all_items = recommendations["weekly"] + recommendations["biweekly"] + recommendations["monthly"]

    for item in all_items:
        food_lower = item["item"].lower()
        assigned = False

        # Check each section's keywords
        for section, keywords in section_map.items():
            if any(keyword in food_lower for keyword in keywords):
                sections[section].append(item)
                assigned = True
                break

        # If not assigned, put in Pantry as default
        if not assigned:
            sections["Pantry & Dry Goods"].append(item)

    # Remove empty sections
    return {section: items for section, items in sections.items() if items}
