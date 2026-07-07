#!/usr/bin/env python3
"""CLI for the 'crue' skill: nearby hydrometric stations and river level/trend, via Hub'Eau."""
import argparse
import json
import os
import sys

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(os.path.dirname(SKILL_DIR))
sys.path.insert(0, PLUGIN_ROOT)

from common.hydro import find_nearby_stations, get_recent_observations, summarize_trend  # noqa: E402


def cmd_stations(args):
    result = find_nearby_stations(args.lat, args.lon, radius_km=args.radius_km)
    print(json.dumps({"source": "Hub'Eau hydrometrie (referentiel stations)", "stations": result}, ensure_ascii=False))


def cmd_niveau(args):
    station_label = None
    if args.station:
        code_station = args.station
    else:
        stations = find_nearby_stations(args.lat, args.lon, radius_km=args.radius_km, limit=1)
        if isinstance(stations, dict) and "error" in stations:
            print(json.dumps(stations, ensure_ascii=False))
            return
        if not stations:
            print(json.dumps({"error": "aucune station hydrometrique active trouvee dans le rayon donne"}, ensure_ascii=False))
            return
        station_label = stations[0]
        code_station = station_label["code_station"]

    observations = get_recent_observations(code_station, n=args.n)
    if isinstance(observations, dict) and "error" in observations:
        print(json.dumps(observations, ensure_ascii=False))
        return

    trend = summarize_trend(observations)
    print(json.dumps({
        "source": "Hub'Eau hydrometrie (donnee Vigicrues federee)",
        "note": "hauteur d'eau relative au repere local de la station, pas une profondeur absolue",
        "code_station": code_station,
        "station": station_label,
        **trend,
    }, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_stations = sub.add_parser("stations", help="list active hydrometric stations near a point")
    p_stations.add_argument("--lat", type=float, required=True)
    p_stations.add_argument("--lon", type=float, required=True)
    p_stations.add_argument("--radius-km", type=float, default=15)

    p_niveau = sub.add_parser("niveau", help="current river level and trend")
    p_niveau.add_argument("--lat", type=float)
    p_niveau.add_argument("--lon", type=float)
    p_niveau.add_argument("--station", type=str, help="Hub'Eau code_station, skips the nearest-station lookup")
    p_niveau.add_argument("--radius-km", type=float, default=15)
    p_niveau.add_argument("--n", type=int, default=12, help="number of recent observations to base the trend on")

    args = parser.parse_args()
    if args.command == "stations":
        cmd_stations(args)
    elif args.command == "niveau":
        if not args.station and (args.lat is None or args.lon is None):
            parser.error("niveau requires either --station or both --lat and --lon")
        cmd_niveau(args)


if __name__ == "__main__":
    main()
