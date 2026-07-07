"""Hub'Eau hydrometrie helpers: real-time river level data (this is the federated Vigicrues feed)."""
from datetime import datetime

from common.geo import haversine_km
from common.http import get_json

STATIONS_URL = "https://hubeau.eaufrance.fr/api/v2/hydrometrie/referentiel/stations"
OBSERVATIONS_URL = "https://hubeau.eaufrance.fr/api/v2/hydrometrie/observations_tr"

# Rough deg/km conversion, fine for building a search bbox (not for precise distance).
BBOX_DEGREES_PER_KM = 1 / 111.0


def find_nearby_stations(lat, lon, radius_km=15, limit=5):
    delta = radius_km * BBOX_DEGREES_PER_KM
    bbox = f"{lon - delta},{lat - delta},{lon + delta},{lat + delta}"
    data = get_json(STATIONS_URL, params={
        "bbox": bbox,
        "size": 50,
        "fields": "code_station,libelle_station,libelle_cours_eau,libelle_commune,longitude_station,latitude_station,en_service",
    })
    if "error" in data:
        return data

    stations = []
    for s in data.get("data", []):
        if not s.get("en_service"):
            continue
        distance = haversine_km(lat, lon, s["latitude_station"], s["longitude_station"])
        stations.append({
            "code_station": s["code_station"],
            "nom": s["libelle_station"],
            "cours_eau": s.get("libelle_cours_eau"),
            "commune": s.get("libelle_commune"),
            "distance_km": round(distance, 2),
        })
    stations.sort(key=lambda s: s["distance_km"])
    return stations[:limit]


def get_recent_observations(code_station, n=12):
    data = get_json(OBSERVATIONS_URL, params={
        "code_entite": code_station,
        "grandeur_hydro": "H",
        "size": n,
        "sort": "desc",
    })
    if "error" in data:
        return data
    return data.get("data", [])


def summarize_trend(observations):
    if not observations:
        return {"tendance": "inconnue", "raison": "aucune observation disponible pour cette station"}

    latest, oldest = observations[0], observations[-1]
    t_latest = datetime.fromisoformat(latest["date_obs"].replace("Z", "+00:00"))
    t_oldest = datetime.fromisoformat(oldest["date_obs"].replace("Z", "+00:00"))
    hours = (t_latest - t_oldest).total_seconds() / 3600
    delta_mm = latest["resultat_obs"] - oldest["resultat_obs"]
    taux_mm_h = round(delta_mm / hours, 1) if hours > 0 else 0.0

    if abs(taux_mm_h) < 5:
        tendance = "stable"
    elif taux_mm_h > 0:
        tendance = "hausse"
    else:
        tendance = "baisse"

    return {
        "hauteur_actuelle_mm": latest["resultat_obs"],
        "date_derniere_mesure": latest["date_obs"],
        "tendance": tendance,
        "taux_variation_mm_par_heure": taux_mm_h,
        "fenetre_analysee_heures": round(hours, 2),
    }
