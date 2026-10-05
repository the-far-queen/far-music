"""
gate.py — CLI wrapper around track.gate().
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from track import compile_track, gate, track_to_dict  # noqa: E402


def _load(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    out = {}
    for line in text.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
            val = val[1:-1]
        if val.startswith("[") and val.endswith("]"):
            items = val[1:-1].split(",")
            val = [i.strip().strip('"').strip("'") for i in items if i.strip()]
        elif isinstance(val, str):
            if val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False
        out[key] = val
    return out


def main(argv):
    p = argparse.ArgumentParser(description="Check the far-music commit_asset gate.")
    p.add_argument("track", help="Path to track YAML/JSON file.")
    p.add_argument("--asset", default="", help="Path to asset text file (banned_term check).")
    args = p.parse_args(argv)

    path = Path(args.track)
    if not path.exists():
        print(f"error: {path} does not exist", file=sys.stderr)
        return 2

    try:
        axes = _load(path)
        track = compile_track(axes)
    except (KeyError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    asset_text = ""
    if args.asset:
        ap = Path(args.asset)
        if not ap.exists():
            print(f"error: asset {ap} does not exist", file=sys.stderr)
            return 2
        asset_text = ap.read_text(encoding="utf-8")

    allow, reason = gate(track, asset_text)
    out = {
        "track_id": track.track_id,
        "allow": allow,
        "reason": reason,
    }
    print(json.dumps(out, indent=2))
    return 0 if allow else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))