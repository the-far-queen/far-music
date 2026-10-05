---
name: track-schema
description: >-
  Use when the user wants to compile a music track, run the M gate, or load public-domain
  source discipline. Triggers: "music track", "track axes", "compile track", "M gate",
  "imslp", "freesound", "mozart k545".
---

# Track schema (far-music)

The track is the **canonical unit** of music in this repo. Every track is a frozen dataclass with a deterministic id.

## Compile

```python
from far_music.tools.track import compile_track, gate

track = compile_track({
    "genre": "classical",
    "bpm": 132,
    "key": "C",
    "mode": "major",
    "time_signature": "4/4",
    "vocal_range": "instrumental",
    "instrument_set": ["solo_piano"],
    "mix_profile": "natural",
    "master_target": "broadcast_-14",
    "royalty_mode": "public_domain",
    "source_id": "imslp/mozart/k545",
})
```

The track_id is `sha256(canonical(axes))[:16]`. Same axes → same id. The tempo_bucket is auto-derived from bpm (allegro for 132).

## Gate

```python
allow, reason = gate(track, asset_text="...")
```

`commit_asset="gate"` refuses naked tracks (`no_track`) or tracks without `source_id` (`no_source_id`) or with invalid `royalty_mode`. `banned_terms` matches against asset text.

## Public-domain sources

See `docs/sources.md` in the repo. imslp + mutopiaproject + freesound (CC0) + wikimedia commons + komplete commons.

## See also

- `AGENTS.md` in the repo — the contract
- `tests/test_track.py` — M1..M5
- `examples/example-mozart-sonata.py` — worked example