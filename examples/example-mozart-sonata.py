"""
example-mozart-sonata.py — public-domain classical track compiled via
far-music pipeline. Demonstrates the track gate.

Source: imslp — W.A. Mozart, Piano Sonata No. 16 in C major, K.545
        (public domain — composer died >100 years ago)
URL:    https://imslp.org/wiki/Piano_Sonata_No.16_in_C_major,_K.545_(Mozart,_Wolfgang_Amadeus)
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "tools"))

from track import compile_track, gate  # noqa: E402

axes = {
    "genre": "classical",
    "bpm": 132,
    "key": "C",
    "mode": "major",
    "time_signature": "4/4",
    "length_target_sec": 300.0,
    "vocal_range": "instrumental",
    "instrument_set": ["solo_piano"],
    "mix_profile": "natural",
    "master_target": "broadcast_-14",
    "lyric_language": "none",
    "lyric_register": "narrative",
    "royalty_mode": "public_domain",
    "source_id": "imslp/mozart/k545",
    "tool_id": "imslp-pipeline",
    "commit_asset": "gate",
}

track = compile_track(axes)

print(f"track_id:    {track.track_id}")
print(f"genre:       {track.genre}")
print(f"bpm:         {track.bpm}")
print(f"key/mode:    {track.key} {track.mode}")
print(f"tempo:       {track.tempo_bucket}")
print(f"length:      {track.length_target_sec}s")
print(f"instruments: {track.instrument_set}")
print(f"royalty:     {track.royalty_mode}")
print()

allow, reason = gate(track)
print(f"gate: allow={allow}, reason={reason}")

allow, reason = gate(None)
print(f"gate(naked): allow={allow}, reason={reason}")

track2 = compile_track(axes)
assert track.track_id == track2.track_id, "must be deterministic"
print(f"\ndeterministic: ✓")