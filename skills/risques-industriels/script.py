#!/usr/bin/env python3
"""CLI for the 'risques-industriels' skill: ICPE/SEVESO sites near a point, via Georisques."""
import argparse
import json
import os
import sys

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(os.path.dirname(SKILL_DIR))
sys.path.insert(0, PLUGIN_ROOT)

from common.georisques import sites_near  # noqa: E402


def cmd_proches(args):
    """Print ICPE/Seveso sites near a point."""
    result = sites_near(args.lat, args.lon, radius_m=args.radius_m, tous=args.tous)
    if isinstance(result, dict) and "error" in result:
        print(json.dumps(result, ensure_ascii=False))
        return
    print(json.dumps({
        "source": "Georisques (installations classees)",
        "lat": args.lat,
        "lon": args.lon,
        "rayon_m": min(args.radius_m, 20000),
        "mode": "toutes les ICPE" if args.tous else "sites Seveso uniquement",
        **result,
    }, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_proches = sub.add_parser("proches", help="ICPE/SEVESO sites near a point")
    p_proches.add_argument("--lat", type=float, required=True)
    p_proches.add_argument("--lon", type=float, required=True)
    p_proches.add_argument("--radius-m", type=int, default=5000, help="max ~20000 (API limit)")
    p_proches.add_argument("--tous", action="store_true", help="include all ICPE, not just Seveso sites")

    args = parser.parse_args()
    if args.command == "proches":
        cmd_proches(args)


if __name__ == "__main__":
    main()
