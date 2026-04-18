from vegetarian_analysis import is_complete_day, is_vegetarian_day
from datetime import timedelta


def longest_vegetarian_streak(nutrition_df):
    """
    Find the longest consecutive vegetarian days.
    Incomplete days break the streak.

    Returns dict with streak length and date range.
    """
    nutrition_df = nutrition_df.copy()
    nutrition_df["date"] = nutrition_df["Date"].dt.date

    dates = sorted(nutrition_df["date"].unique())

    max_streak = 0
    current_streak = 0
    streak_start = None
    max_streak_start = None
    max_streak_end = None

    for date in dates:
        if is_complete_day(nutrition_df, date) and is_vegetarian_day(nutrition_df, date):
            if current_streak == 0:
                streak_start = date
            current_streak += 1
        else:
            if current_streak > max_streak:
                max_streak = current_streak
                max_streak_start = streak_start
                max_streak_end = date - timedelta(days=1)
            current_streak = 0

    # Check if the last streak is the longest
    if current_streak > max_streak:
        max_streak = current_streak
        max_streak_start = streak_start
        max_streak_end = dates[-1]

    return {
        "length": max_streak,
        "start_date": max_streak_start,
        "end_date": max_streak_end,
    }


def all_vegetarian_streaks(nutrition_df):
    """
    Find all vegetarian streaks (length >= 2 days).
    Returns list of dicts with streak info.
    """
    nutrition_df = nutrition_df.copy()
    nutrition_df["date"] = nutrition_df["Date"].dt.date

    dates = sorted(nutrition_df["date"].unique())
    streaks = []

    current_streak = 0
    streak_start = None

    for date in dates:
        if is_complete_day(nutrition_df, date) and is_vegetarian_day(nutrition_df, date):
            if current_streak == 0:
                streak_start = date
            current_streak += 1
        else:
            if current_streak >= 2:
                streaks.append({
                    "length": current_streak,
                    "start_date": streak_start,
                    "end_date": date - timedelta(days=1),
                })
            current_streak = 0

    # Check last streak
    if current_streak >= 2:
        streaks.append({
            "length": current_streak,
            "start_date": streak_start,
            "end_date": dates[-1],
        })

    return sorted(streaks, key=lambda x: x["length"], reverse=True)
