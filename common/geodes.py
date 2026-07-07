"""Sanitary surveillance data (Sante publique France).

Geodes (geodes.santepubliquefrance.fr) redirects to odisse.santepubliquefrance.fr, a
standard OpenDataSoft instance with a documented, self-describing API (no key needed) --
confirmed while building this skill, after Sentiweb's undocumented API resisted
reverse-engineering. Data is weekly, at department granularity.
"""
from common.http import get_json

DATASET_URL = (
    "https://odisse.santepubliquefrance.fr/api/explore/v2.1/catalog/datasets/"
    "gastro-enterite-aigue-passages-aux-urgences-et-actes-sos-medecins-departement/records"
)


def get_gastro_enterite_trend(code_departement, weeks=8):
    data = get_json(DATASET_URL, params={
        "where": f'dep="{code_departement}" AND sursaud_cl_age_gene="Tous âges"',
        "order_by": "date_complet desc",
        "limit": weeks,
    })
    if "error" in data:
        return data

    records = data.get("results", [])
    if not records:
        return {"error": f"aucune donnee de surveillance pour le departement {code_departement}"}

    latest, oldest = records[0], records[-1]
    taux_actuel = latest.get("taux_passages_gastro_sau")
    taux_ancien = oldest.get("taux_passages_gastro_sau")

    tendance, variation_pct = "stable", None
    if taux_actuel is not None and taux_ancien:
        variation_pct = round(100 * (taux_actuel - taux_ancien) / taux_ancien, 1)
        if variation_pct > 15:
            tendance = "hausse"
        elif variation_pct < -15:
            tendance = "baisse"

    return {
        "departement": latest.get("libgeo"),
        "code_departement": code_departement,
        "semaine_la_plus_recente": latest.get("semaine"),
        "taux_passages_urgences_gastro_pour_100000": round(taux_actuel, 1) if taux_actuel is not None else None,
        "tendance_sur_periode": tendance,
        "variation_pct": variation_pct,
        "nb_semaines_analysees": len(records),
        "historique": [
            {"semaine": r.get("semaine"), "taux": r.get("taux_passages_gastro_sau")}
            for r in reversed(records)
        ],
    }
