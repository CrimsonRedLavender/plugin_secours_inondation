#!/usr/bin/env python3
"""CLI for the 'veille-sanitaire' skill: acute gastro-enteritis ER-visit trend for a
department (a waterborne-illness proxy relevant post-flood), via Sante publique France."""
import argparse
import json
import os
import sys

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(os.path.dirname(SKILL_DIR))
sys.path.insert(0, PLUGIN_ROOT)

from common.geodes import get_gastro_enterite_trend  # noqa: E402
from common.insee import find_commune  # noqa: E402


def cmd_tendance(args):
    """Print the gastro-enteritis ER-visit trend for a department (given directly, or
    resolved from a point/commune name first)."""
    avertissement = None
    if args.departement:
        code_departement = args.departement
    else:
        commune = find_commune(lat=args.lat, lon=args.lon, nom=args.commune)
        if "error" in commune:
            print(json.dumps(commune, ensure_ascii=False))
            return
        code_departement = commune.get("codeDepartement")
        avertissement = commune.get("avertissement")
        if not code_departement:
            print(json.dumps({"error": "impossible de determiner le departement pour ce point"}, ensure_ascii=False))
            return

    result = get_gastro_enterite_trend(code_departement, weeks=args.semaines)
    if isinstance(result, dict) and "error" in result:
        print(json.dumps(result, ensure_ascii=False))
        return

    if avertissement:
        result["avertissement"] = avertissement

    print(json.dumps({
        "source": "Sante publique France (Odisse) - gastro-enterite aigue, passages aux urgences",
        **result,
    }, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_tendance = sub.add_parser("tendance", help="gastro-enteritis ER visit trend for a department")
    p_tendance.add_argument("--lat", type=float)
    p_tendance.add_argument("--lon", type=float)
    p_tendance.add_argument("--commune", type=str)
    p_tendance.add_argument("--departement", type=str, help="INSEE department code, e.g. 10, 75, 2A")
    p_tendance.add_argument("--semaines", type=int, default=8)

    args = parser.parse_args()
    if args.command == "tendance":
        if not args.departement and args.lat is None and not args.commune:
            parser.error("tendance requires --departement, or --lat/--lon, or --commune")
        cmd_tendance(args)


if __name__ == "__main__":
    main()
