#!/usr/bin/env python3
"""CLI for the 'meteo' skill: rainfall forecast for a point, via Open-Meteo."""
import argparse
import json
import os
import sys

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(os.path.dirname(SKILL_DIR))
sys.path.insert(0, PLUGIN_ROOT)

from common.meteo import get_rain_forecast  # noqa: E402


def cmd_prevision(args):
    result = get_rain_forecast(args.lat, args.lon, hours=args.heures)
    if isinstance(result, dict) and "error" in result:
        print(json.dumps(result, ensure_ascii=False))
        return
    print(json.dumps({"source": "Open-Meteo", **result}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_prevision = sub.add_parser("prevision", help="rainfall forecast for a point")
    p_prevision.add_argument("--lat", type=float, required=True)
    p_prevision.add_argument("--lon", type=float, required=True)
    p_prevision.add_argument("--heures", type=int, default=72, help="forecast horizon in hours (max ~168)")

    args = parser.parse_args()
    if args.command == "prevision":
        cmd_prevision(args)


if __name__ == "__main__":
    main()
