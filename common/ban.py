"""BAN (Base Adresse Nationale) geocoding helpers."""
from common.http import get_json

SEARCH_URL = "https://api-adresse.data.gouv.fr/search/"
REVERSE_URL = "https://api-adresse.data.gouv.fr/reverse/"


def geocode(address):
    """Best-match coordinates for a free-text address.

    Returns {"label", "lat", "lon", "type", "score", "commune", "code_insee"} on success,
    or {"error": "..."}. `score` (0-1) is BAN's own confidence in the match — a high score
    does not guarantee the match is what the caller meant (e.g. "Berlin" resolves to a
    real French hamlet with score ~0.94), so callers must sanity-check it themselves; see
    skills/localisation/SKILL.md for the interpretation rule.
    """
    data = get_json(SEARCH_URL, params={"q": address, "limit": 1})
    if "error" in data:
        return data
    features = data.get("features", [])
    if not features:
        return {"error": f"aucune adresse trouvee pour: {address}"}
    props = features[0]["properties"]
    lon, lat = features[0]["geometry"]["coordinates"]
    return {
        "label": props.get("label"),
        "lat": lat,
        "lon": lon,
        "type": props.get("type"),
        "score": props.get("score"),
        "commune": props.get("city"),
        "code_insee": props.get("citycode"),
    }


def reverse_geocode(lat, lon):
    """Nearest known address label for a lat/lon point, or {"error": "..."}."""
    data = get_json(REVERSE_URL, params={"lat": lat, "lon": lon})
    if "error" in data:
        return data
    features = data.get("features", [])
    if not features:
        return {"error": f"aucune adresse trouvee pres de {lat},{lon}"}
    props = features[0]["properties"]
    return {"label": props.get("label"), "commune": props.get("city"), "code_insee": props.get("citycode")}
