"""Georisques ICPE/SEVESO helpers.

Notes from building this skill: the API has no server-side Seveso filter param (tried
`seveso=` and `statutSeveso=`, both silently ignored), so filtering happens client-side
after paging through results. A radius above ~20-25km reliably returns HTTP 500, so it's
capped here. `latlon` takes "lon,lat" order despite the name, confirmed by testing.
"""
from common.geo import haversine_km
from common.http import get_json

ICPE_URL = "https://georisques.gouv.fr/api/v1/installations_classees"
MAX_RADIUS_M = 20000
MAX_PAGES = 10
PAGE_SIZE = 500
SEVESO_STATUSES = ("Seveso seuil haut", "Seveso seuil bas")


def sites_near(lat, lon, radius_m=5000, tous=False):
    """ICPE sites within radius_m of a point, nearest first.

    By default (tous=False) keeps only Seveso sites (seuil haut/bas); tous=True returns
    every classified installation, Seveso or not. Returns {"sites": [...], "troncature":
    bool} — "troncature" is True if MAX_PAGES was hit and more results may exist but
    weren't fetched (radius_m is itself capped at MAX_RADIUS_M, above which the API
    reliably 500s). Returns {"error": "..."} if the API call failed.
    """
    radius_m = min(radius_m, MAX_RADIUS_M)
    sites, truncated = [], False

    for page in range(1, MAX_PAGES + 1):
        data = get_json(ICPE_URL, params={
            "rayon": radius_m,
            "latlon": f"{lon},{lat}",
            "page": page,
            "page_size": PAGE_SIZE,
        })
        if "error" in data:
            return data

        page_data = data.get("data", [])
        if not page_data:
            break

        for site in page_data:
            statut = site.get("statutSeveso")
            if not tous and statut not in SEVESO_STATUSES:
                continue
            slat, slon = site.get("latitude"), site.get("longitude")
            sites.append({
                "nom": site.get("raisonSociale"),
                "commune": site.get("commune"),
                "adresse": site.get("adresse1"),
                "statut_seveso": statut,
                "regime": site.get("regime"),
                "etat_activite": site.get("etatActivite"),
                "distance_km": round(haversine_km(lat, lon, slat, slon), 2) if slat and slon else None,
            })

        total_pages = data.get("total_pages") or page
        if page >= total_pages:
            break
        if page == MAX_PAGES:
            truncated = True

    sites.sort(key=lambda s: (s["distance_km"] is None, s["distance_km"]))
    return {"sites": sites, "troncature": truncated}
