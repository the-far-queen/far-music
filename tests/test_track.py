"""
test_track.py — M1..M5 gate tests for far-music/tools/track.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "tools"))

from track import compile_track, gate  # noqa: E402


def _base_axes(**overrides):
    axes = {
        "genre": "classical",
        "bpm": 120,
        "key": "C",
        "mode": "major",
        "time_signature": "4/4",
        "vocal_range": "instrumental",
        "instrument_set": ["strings", "woodwinds"],
        "mix_profile": "natural",
        "master_target": "broadcast_-14",
        "lyric_language": "none",
        "lyric_register": "narrative",
        "royalty_mode": "public_domain",
        "source_id": "imslp/score/mozart-k545",
        "commit_asset": "gate",
    }
    axes.update(overrides)
    return axes


def test_M1_repro_id():
    """M1: same axes -> same id; different axes -> different id."""
    a = _base_axes()
    s1 = compile_track(a)
    s2 = compile_track(a)
    s3 = compile_track(_base_axes(bpm=80))
    assert s1.track_id == s2.track_id, "M1: same axes must produce same id"
    assert s1.track_id != s3.track_id, "M1: different axes must produce different id"
    print("M1: ok")


def test_M2_royalty_gate():
    """M2: invalid royalty_mode -> refused; valid pd -> ok."""
    s_pd = compile_track(_base_axes(royalty_mode="public_domain"))
    allow, reason = gate(s_pd)
    assert allow and reason == "ok", f"M2 pd fail: {reason}"

    # bogus royalty mode caught by compile
    try:
        compile_track(_base_axes(royalty_mode="unlicensed_corporate"))
        assert False, "M2: should reject bogus royalty_mode"
    except ValueError:
        pass

    # compile_track doesn't reject because compile is permissive;
    # gate enforces source_id + royalty_mode valid
    s_bogus = compile_track(_base_axes(royalty_mode="public_domain"))
    s_bogus_bad = type(s_bogus)(
        **{**s_bogus.__dict__, "royalty_mode": "unlicensed"}
    )
    allow, reason = gate(s_bogus_bad)
    assert not allow and "royalty_mode_invalid" in reason, f"M2 bogus fail: {reason}"
    print("M2: ok")


def test_M3_ids_survive_reload():
    """M3: deterministic compile from same input."""
    axes = _base_axes()
    s1 = compile_track(axes)
    s2 = compile_track(axes)
    assert s1.track_id == s2.track_id
    assert s1.genre == s2.genre == "classical"
    assert s1.bpm == s2.bpm == 120
    print("M3: ok")


def test_M4_primary_axes_distinct():
    """M4: varying genre/bpm/key -> distinct ids."""
    s_base = compile_track(_base_axes())
    s_genre = compile_track(_base_axes(genre="jazz"))
    s_bpm = compile_track(_base_axes(bpm=160))
    s_key = compile_track(_base_axes(key="D"))
    ids = {s_base.track_id, s_genre.track_id, s_bpm.track_id, s_key.track_id}
    assert len(ids) == 4, f"M4: expected 4 distinct ids, got {len(ids)}"
    print("M4: ok")


def test_M5_no_house_default():
    """M5: naked prompt + gate -> refused, no fallback."""
    allow, reason = gate(None)
    assert not allow and reason == "no_track", f"M5 fail: {reason}"
    s_forbid = compile_track(_base_axes(commit_asset="forbid"))
    allow, reason = gate(s_forbid)
    assert not allow and reason == "commit_forbidden", f"M5 forbid fail: {reason}"
    print("M5: ok")


def main():
    test_M1_repro_id()
    test_M2_royalty_gate()
    test_M3_ids_survive_reload()
    test_M4_primary_axes_distinct()
    test_M5_no_house_default()
    print("\nALL M1..M5 PASS")


if __name__ == "__main__":
    main()