#!/usr/bin/env python3
"""CLI for the 'demographie-vulnerabilite' skill: population, density and age-based
vulnerability (share of elderly residents) for a commune, via geo.api.gouv.fr + INSEE melodi."""
import argparse
import json
import os
import sys

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(os.path.dirname(SKILL_DIR))
sys.path.insert(0, PLUGIN_ROOT)

from common.insee import find_commune, get_age_breakdown  # noqa: E402


def cmd_profil(args):
    commune = find_commune(lat=args.lat, lon=args.lon, nom=args.commune)
    if "error" in commune:
        print(json.dumps(commune, ensure_ascii=False))
        return

    surface_km2 = commune["surface"] / 100 if commune.get("surface") else None
    densite = round(commune["population"] / surface_km2, 1) if surface_km2 else None

    age_breakdown = get_age_breakdown(commune["code"], annee=args.annee)

    output = {
        "source": "geo.api.gouv.fr (population/surface) + INSEE melodi (structure par age)",
        "commune": commune["nom"],
        "code_insee": commune["code"],
        "population": commune["population"],
        "surface_km2": round(surface_km2, 1) if surface_km2 else None,
        "densite_hab_km2": densite,
        "structure_age": age_breakdown,
    }
    if "avertissement" in commune:
        output["avertissement"] = commune["avertissement"]
    print(json.dumps(output, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_profil = sub.add_parser("profil", help="population, density and age-based vulnerability for a commune")
    p_profil.add_argument("--lat", type=float)
    p_profil.add_argument("--lon", type=float)
    p_profil.add_argument("--commune", type=str, help="commune name, used if --lat/--lon are not given")
    p_profil.add_argument("--annee", type=int, default=2023)

    args = parser.parse_args()
    if args.command == "profil":
        if args.lat is None and args.lon is None and not args.commune:
            parser.error("profil requires either --lat/--lon or --commune")
        cmd_profil(args)


if __name__ == "__main__":
    main()
