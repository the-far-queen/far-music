# AGENTS.md — (far-music repo)

> A track is not a vibe.

This file is the contract. Every commit gate checks against it.
Every track references it. Every test (M1..M5) reads it.

If you change the schema, update AGENTS.md first. The repo is downstream
of this file.

## What this repo is

songs, albums, stems, sheet music, lyric sheets, production notes, the music pipeline.

## Packet

```
track  Track | AssetRef
```

**No asset without `track_id` + `hash`.** The gate refuses naked assets.

## Error this repo exists to stop

conflating every track into one house sound. 'Make it vibey' is not an axis. Genre, BPM, key, and vocal range are.

## Axes

music-pipeline axes: genre, bpm, key, mode, time-signature, vocal-range, instrument-set, mix-profile, master-target, lyric-language, lyric-register, banned-terms, source-discipline, royalty-mode, length-target.

The schema is in the pipeline source (`tools/sheet.py`). Axes are the
contract; vibe is not.

## Surface

```python
track.compile(axes) -> Track
stems.from_track(track)
sheet.from_track(track)
lyric.fit(track, lyrics)
mix.profile(track, profile_id)
```

## Gate

`commit_asset` defaults to `{gate}`. The gate checks:

1. `track_id` is set.
2. `track_id == sha256(canonical(axes))`.
3. `variant_of` (if set) is a known parent.
4. No banned-motifs present.
5. Source-discipline: every claim links to a source.

A naked track (no `track_id`) is refused with reason `no_track`.

## Tests

| # | Test | What it checks |
|---|---|---|
| M1 | repro id | Track with same axes -> same id; different axes -> different id. |
| M2 | banned terms rejected | Track with banned-terms + asset containing them -> refused. |
| M3 | ids survive restart | Compile + serialize + deserialize -> all ids preserved. |
| M4 | two different settings cannot share id | Vary primary axes -> different id. |
| M5 | prompt without track does not apply house | Naked prompt + gate -> refused, no fallback to default. |

## Anti-patterns

- house-sound default
- vibe without genre
- samples without royalty-mode
- lyrics without source-discipline.

## Related

- the-far-queen/far-art (style substrate), the-far-queen/far-film (video sync), the-far-queen/simself (MLTR for lyrics)

## License

MIT. Free for all agents, human and non-human.
