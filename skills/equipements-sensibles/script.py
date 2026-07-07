#!/usr/bin/env python3
"""CLI for the 'equipements-sensibles' skill: hospitals, EHPAD, schools and fire stations
near a point, via OpenStreetMap/Overpass."""
import argparse
import json
import os
import sys

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(os.path.dirname(SKILL_DIR))
sys.path.insert(0, PLUGIN_ROOT)

from common.overpass import facilities_near  # noqa: E402

CATEGORIES = {
    "hopitaux": '["amenity"="hospital"]',
    "ehpad": '["amenity"="social_facility"]["social_facility"="nursing_home"]',
    "ecoles": '["amenity"~"^(school|kindergarten)$"]',
    "casernes_pompiers": '["amenity"="fire_station"]',
}


def cmd_proches(args):
    """Print sensitive facilities near a point, for one category or all of them."""
    categories = CATEGORIES if args.categorie == "tous" else {args.categorie: CATEGORIES[args.categorie]}
    result = {}
    for name, tag_filter in categories.items():
        facilities = facilities_near(tag_filter, args.lat, args.lon, radius_m=args.radius_m, limit=args.limit)
        if isinstance(facilities, dict) and "error" in facilities:
            print(json.dumps({"error": f"echec sur '{name}': {facilities['error']}"}, ensure_ascii=False))
            return
        result[name] = facilities

    print(json.dumps({
        "source": "OpenStreetMap / Overpass API",
        "lat": args.lat,
        "lon": args.lon,
        "rayon_m": args.radius_m,
        "equipements": result,
    }, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_proches = sub.add_parser("proches", help="sensitive facilities near a point")
    p_proches.add_argument("--lat", type=float, required=True)
    p_proches.add_argument("--lon", type=float, required=True)
    p_proches.add_argument("--radius-m", type=int, default=1500)
    p_proches.add_argument("--categorie", choices=[*CATEGORIES.keys(), "tous"], default="tous")
    p_proches.add_argument("--limit", type=int, default=15)

    args = parser.parse_args()
    if args.command == "proches":
        cmd_proches(args)


if __name__ == "__main__":
    main()
