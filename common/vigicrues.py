"""Vigicrues vigilance-level helpers: official color code (vert/jaune/orange/rouge) per
monitored river section ("troncon").

No API key needed. There is no reliable API-side join between a Hub'Eau station and its
parent vigilance section: the field meant for that (`aNPlusUn.CdEntVigiCruSuperieur` on
https://www.vigicrues.gouv.fr/services/v1.1/StaEntVigiCru.json) comes back unfilled
("A renseigner") even for a real, actively-monitored station — confirmed while building
this. Nearest-section is found by geometry instead: matching the point against the
closest vertex of each section's line geometry. Section geometries are dense enough for
this to be accurate in practice (confirmed on Paris: correctly found "Seine a Paris" at
190m instead of a farther section).

Only ~340 sections cover metropolitan France (the major rivers monitored by the state,
not every stream) — a point far from all of them means no coverage, not "no risk".
"""
from common.geo import haversine_km
from common.http import get_json

GEOJSON_URL = "http://www.vigicrues.gouv.fr/services/1/InfoVigiCru.geojson"

NIVEAU_LABELS = {1: "vert", 2: "jaune", 3: "orange", 4: "rouge"}

# Sections are spaced unevenly; beyond this, treat "nearest section" as no real coverage
# rather than presenting a distant section's color as if it applied here.
MAX_DISTANCE_KM = 30


def _min_distance_to_line(lat, lon, coordinates):
    """Approximate point-to-line distance as the min distance to any of its vertices.

    Not an exact point-to-segment distance, but the section geometries are dense enough
    (vertices every few hundred meters along the river) that the approximation error is
    negligible in practice — confirmed on Paris (correct section found at 190m).
    """
    return min(haversine_km(lat, lon, pt[1], pt[0]) for pt in coordinates)


def find_nearest_vigilance(lat, lon):
    """Return the Vigicrues vigilance color of the section nearest to (lat, lon).

    On success: {"troncon", "niveau_vigilance" (1-4), "couleur_vigilance", "distance_km"}.
    On failure (API unreachable, or nothing within MAX_DISTANCE_KM): {"error": "..."}.
    """
    data = get_json(GEOJSON_URL)
    if "error" in data:
        return data

    features = data.get("features", [])
    best = None
    for feature in features:
        geometry = feature.get("geometry", {})
        # Defensive: the feed is documented as MultiLineString only, but skip anything
        # else rather than let a malformed/unexpected feature crash the whole lookup.
        if geometry.get("type") != "MultiLineString":
            continue
        lines = geometry.get("coordinates", [])
        if not lines:
            continue
        distance = min(_min_distance_to_line(lat, lon, line) for line in lines)
        if best is None or distance < best[0]:
            best = (distance, feature.get("properties", {}))

    if best is None:
        return {"error": "aucune donnee de vigilance crues disponible"}

    distance, props = best
    if distance > MAX_DISTANCE_KM:
        return {
            "error": f"aucun troncon de vigilance crues surveille par l'Etat a moins de {MAX_DISTANCE_KM}km "
                     f"(le plus proche, '{props.get('lbentcru')}', est a {round(distance, 1)}km) "
                     "— Vigicrues ne couvre que les principaux cours d'eau, pas tous les ruisseaux"
        }

    niveau = props.get("NivInfViCr")
    return {
        "troncon": props.get("lbentcru"),
        "niveau_vigilance": niveau,
        "couleur_vigilance": NIVEAU_LABELS.get(niveau, "inconnu"),
        "distance_km": round(distance, 2),
    }
