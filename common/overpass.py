"""Overpass API (OpenStreetMap) helpers: roads, bridges, water access near a point.

Note: `natural=water` (lakes, riverbanks) is deliberately not queried here — those are
often huge multipolygon relations (e.g. an entire river's bank) that the public Overpass
instance rejects outright (HTTP 406), confirmed while building this skill. `waterway=*`
(river/stream/canal center-lines) covers the "acces a l'eau" need without that failure mode.
"""
from common.geo import haversine_km
from common.http import get_json

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Every query below declares [timeout:20] server-side (how long Overpass may compute);
# the client timeout must exceed that or we cut the connection before the server replies
# with a valid (slow but successful) answer, confirmed while building this skill.
CLIENT_TIMEOUT = 25


def _run(query):
    data = get_json(OVERPASS_URL, params={"data": query}, timeout=CLIENT_TIMEOUT)
    if "error" in data:
        return data
    return data.get("elements", [])


def facilities_near(tag_filter, lat, lon, radius_m=1500, limit=15):
    """Points of interest matching an Overpass tag filter (e.g. '["amenity"="hospital"]').

    Queries both node and way, since facilities are inconsistently mapped in OSM — e.g.
    fire stations in Paris are tagged as way (building outlines), not node, confirmed
    while building this skill. A node-only query silently misses them.
    """
    query = (
        f'[out:json][timeout:20];'
        f'(node{tag_filter}(around:{radius_m},{lat},{lon});'
        f'way{tag_filter}(around:{radius_m},{lat},{lon}););'
        f'out tags center {limit};'
    )
    elements = _run(query)
    if isinstance(elements, dict):
        return elements

    results = []
    for el in elements:
        tags = el.get("tags", {})
        if el["type"] == "node":
            elat, elon = el.get("lat"), el.get("lon")
        else:
            center = el.get("center", {})
            elat, elon = center.get("lat"), center.get("lon")
        results.append({
            "nom": tags.get("name", "sans nom"),
            "lat": elat,
            "lon": elon,
            "distance_km": round(haversine_km(lat, lon, elat, elon), 2) if elat and elon else None,
            "telephone": tags.get("phone") or tags.get("contact:phone"),
        })
    results.sort(key=lambda r: (r["distance_km"] is None, r["distance_km"]))
    return results


def roads_near(lat, lon, radius_m=800, limit=15):
    query = f'[out:json][timeout:20];way["highway"](around:{radius_m},{lat},{lon});out tags {limit};'
    elements = _run(query)
    if isinstance(elements, dict):
        return elements
    names, seen = [], set()
    for el in elements:
        name = el.get("tags", {}).get("name")
        if name and name not in seen:
            seen.add(name)
            names.append(name)
    return names


def bridges_near(lat, lon, radius_m=1500, limit=10):
    query = f'[out:json][timeout:20];way["bridge"="yes"](around:{radius_m},{lat},{lon});out tags {limit};'
    elements = _run(query)
    if isinstance(elements, dict):
        return elements
    bridges = []
    for el in elements:
        tags = el.get("tags", {})
        bridges.append({"nom": tags.get("name", "sans nom"), "type": tags.get("highway") or tags.get("railway")})
    return bridges


def water_access_near(lat, lon, radius_m=1500, limit=10):
    query = (
        f'[out:json][timeout:20];'
        f'way["waterway"~"^(river|stream|canal)$"](around:{radius_m},{lat},{lon});'
        f'out tags {limit};'
    )
    elements = _run(query)
    if isinstance(elements, dict):
        return elements
    seen, points = set(), []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name", "cours d'eau sans nom")
        key = (name, tags.get("waterway"))
        if key not in seen:
            seen.add(key)
            points.append({"nom": name, "type": tags.get("waterway")})
    return points


def buildings_count_near(lat, lon, radius_m=300):
    query = f'[out:json][timeout:20];way["building"](around:{radius_m},{lat},{lon});out count;'
    elements = _run(query)
    if isinstance(elements, dict):
        return elements
    for el in elements:
        if el.get("type") == "count":
            return int(el["tags"]["total"])
    return 0
