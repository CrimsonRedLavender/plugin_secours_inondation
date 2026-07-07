#!/usr/bin/env python3
"""CLI for the 'localisation' skill: geocode an address, or characterize access around a point
(roads, bridges, water access, building density) via BAN + Overpass."""
import argparse
import json
import os
import sys

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(os.path.dirname(SKILL_DIR))
sys.path.insert(0, PLUGIN_ROOT)

from common.ban import geocode, reverse_geocode  # noqa: E402
from common.overpass import bridges_near, buildings_count_near, roads_near, water_access_near  # noqa: E402


def cmd_geocode(args):
    result = geocode(args.address)
    print(json.dumps({"source": "BAN (api-adresse.data.gouv.fr)", **wrap(result)}, ensure_ascii=False))


def cmd_reverse(args):
    result = reverse_geocode(args.lat, args.lon)
    print(json.dumps({"source": "BAN (api-adresse.data.gouv.fr)", **wrap(result)}, ensure_ascii=False))


def cmd_acces(args):
    routes = roads_near(args.lat, args.lon, radius_m=args.radius_m)
    ponts = bridges_near(args.lat, args.lon, radius_m=args.radius_m * 2)
    points_eau = water_access_near(args.lat, args.lon, radius_m=args.radius_m * 2)
    nb_batiments = buildings_count_near(args.lat, args.lon, radius_m=args.radius_m)

    for label, value in [("routes", routes), ("ponts", ponts), ("points_eau", points_eau), ("nb_batiments", nb_batiments)]:
        if isinstance(value, dict) and "error" in value:
            print(json.dumps({"error": f"echec sur '{label}': {value['error']}"}, ensure_ascii=False))
            return

    print(json.dumps({
        "source": "OpenStreetMap / Overpass API",
        "lat": args.lat,
        "lon": args.lon,
        "rayon_m": args.radius_m,
        "routes": routes,
        "ponts": ponts,
        "points_eau": points_eau,
        "nb_batiments_dans_le_rayon": nb_batiments,
    }, ensure_ascii=False))


def wrap(result):
    if isinstance(result, dict) and "error" in result:
        return result
    return {"resultat": result}


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_geocode = sub.add_parser("geocode", help="turn an address into coordinates")
    p_geocode.add_argument("--address", type=str, required=True)

    p_reverse = sub.add_parser("reverse", help="turn coordinates into an address")
    p_reverse.add_argument("--lat", type=float, required=True)
    p_reverse.add_argument("--lon", type=float, required=True)

    p_acces = sub.add_parser("acces", help="roads, bridges, water access and building density around a point")
    p_acces.add_argument("--lat", type=float, required=True)
    p_acces.add_argument("--lon", type=float, required=True)
    p_acces.add_argument("--radius-m", type=int, default=800)

    args = parser.parse_args()
    if args.command == "geocode":
        cmd_geocode(args)
    elif args.command == "reverse":
        cmd_reverse(args)
    elif args.command == "acces":
        cmd_acces(args)


if __name__ == "__main__":
    main()
