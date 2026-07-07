"""Commune lookup (geo.api.gouv.fr) and age-breakdown (INSEE melodi) helpers.

geo.api.gouv.fr gives population/surface directly per commune, no key required.
INSEE melodi's DS_RP_POPULATION_PRINC dataset gives age brackets per commune when
filtered with GEO=COM-<code_insee>, also no key required — confirmed while building
this skill. The dataset uses SDMX-style dimension codes (Y_GE65 = 65 and older, etc.)
and carries multiple census years; 2023 is the latest available as of writing.
"""
import unicodedata

from common.http import get_json

GEO_API_URL = "https://geo.api.gouv.fr/communes"
MELODI_URL = "https://api.insee.fr/melodi/data/DS_RP_POPULATION_PRINC"


def _normalize(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return "".join(c for c in text if c.isalnum())


def find_commune(lat=None, lon=None, nom=None):
    params = {"fields": "nom,code,codeDepartement,population,surface,centre"}
    if lat is not None and lon is not None:
        params["lat"] = lat
        params["lon"] = lon
    elif nom:
        params["nom"] = nom
        params["boost"] = "population"
        params["limit"] = 1
    else:
        return {"error": "il faut fournir soit lat/lon, soit un nom de commune"}

    data = get_json(GEO_API_URL, params=params)
    if isinstance(data, dict) and "error" in data:
        return data
    if not data:
        return {"error": "commune introuvable"}

    result = data[0]
    # The API's fuzzy name search can match a near-miss (e.g. "Berlin" -> "Berling", a
    # 313-inhabitant French hamlet) instead of failing, and its relevance _score is
    # population-boosted so it can't be used to detect this — confirmed while building
    # this skill. Flag a non-exact match explicitly instead of returning it silently.
    if nom and _normalize(result["nom"]) != _normalize(nom):
        result["avertissement"] = (
            f"aucune commune francaise ne correspond exactement a '{nom}' ; "
            f"resultat le plus proche trouve : '{result['nom']}' — verifier qu'il s'agit "
            f"bien de la commune recherchee avant d'utiliser ces donnees"
        )
    return result


def get_age_breakdown(code_insee, annee=2023):
    data = get_json(MELODI_URL, params={"GEO": f"COM-{code_insee}", "SEX": "_T", "TIME_PERIOD": str(annee)})
    if "error" in data:
        return data
    observations = data.get("observations", [])
    if not observations:
        return {"error": f"aucune donnee INSEE pour la commune {code_insee} en {annee}"}

    values = {obs["dimensions"]["AGE"]: obs["measures"]["OBS_VALUE_NIVEAU"]["value"] for obs in observations}
    total = values.get("_T")

    result = {"annee": annee, "population_totale_insee": round(total) if total else None}
    if total:
        for key, label in (("Y_GE65", "65_ans_et_plus"), ("Y_GE80", "80_ans_et_plus"), ("Y_LT15", "moins_15_ans")):
            value = values.get(key)
            if value is not None:
                result[f"part_{label}_pct"] = round(100 * value / total, 1)
                result[f"personnes_{label}"] = round(value)
    return result
