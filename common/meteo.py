"""Open-Meteo helpers: rainfall forecast for a point (no API key required).

Note: "now" comes from the API's own `current.time` field, not the local machine clock —
the hourly array always starts at 00:00 of the current day, so slicing forward needs the
API's own notion of "now" in the request's timezone to avoid summing past hours.
"""
from common.http import get_json

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def get_rain_forecast(lat, lon, hours=72):
    forecast_days = max(1, min(7, (hours // 24) + 2))
    data = get_json(FORECAST_URL, params={
        "latitude": lat,
        "longitude": lon,
        "current": "precipitation,rain",
        "hourly": "precipitation",
        "forecast_days": forecast_days,
        "timezone": "Europe/Paris",
    })
    if "error" in data:
        return data

    now = data["current"]["time"]
    times = data["hourly"]["time"]
    values = data["hourly"]["precipitation"]

    # `current.time` has 15-min precision (e.g. "...T10:30") but the hourly array only
    # has on-the-hour entries ("...T10:00") — an exact match fails and silently falls
    # back to midnight, confirmed while building this skill. Round down to the hour.
    now_hour = now[:13] + ":00"
    try:
        start_index = times.index(now_hour)
    except ValueError:
        start_index = 0

    upcoming = values[start_index:start_index + hours]
    upcoming_times = times[start_index:start_index + hours]

    checkpoints = {}
    for h in (24, 48, 72):
        if h <= len(upcoming):
            checkpoints[f"cumul_{h}h_mm"] = round(sum(upcoming[:h]), 1)

    pic_mm = max(upcoming) if upcoming else 0.0
    pic_index = upcoming.index(pic_mm) if upcoming else None

    return {
        "maintenant": now,
        "precipitation_actuelle_mm": data["current"]["precipitation"],
        "cumul_total_periode_mm": round(sum(upcoming), 1),
        "periode_analysee_heures": len(upcoming),
        **checkpoints,
        "pic_horaire_mm": pic_mm,
        "heure_du_pic": upcoming_times[pic_index] if pic_index is not None else None,
    }
