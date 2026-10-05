"""
track.py — Track compile + gate (far-music).

Mirrors far-film/tools/shot.py structure. The schema (axes) is the
contract declared in AGENTS.md. Naked tracks (no track_id) are refused
with reason 'no_track'. Banned terms are refused with reason
'banned_term'.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Enums (the contract — see AGENTS.md)
# ---------------------------------------------------------------------------

# Tempo buckets (BPM)
TEMPO_BUCKETS = {"grave", "largo", "adagio", "andante", "allegretto",
                 "moderato", "allegro", "presto", "prestissimo"}
# Genre buckets (non-exhaustive — add as needed)
GENRES = {"classical", "baroque", "romantic", "modern", "jazz", "blues",
          "folk", "country", "rock", "metal", "punk", "electronic",
          "ambient", "hiphop", "rap", "rnb", "soul", "funk", "reggae",
          "ska", "latin", "world", "experimental", "soundtrack", "spoken",
          "chant", "liturgical", "choral", "opera", "musical"}
# Keys
KEYS = {"C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"}
# Modes
MODES = {"major", "minor", "dorian", "phrygian", "lydian", "mixolydian",
         "aeolian", "locrian", "harmonic_minor", "melodic_minor",
         "church_modes", "modal", "atonal"}
# Time signatures
TIME_SIGNATURES = {"4/4", "3/4", "2/4", "6/8", "9/8", "12/8", "5/4", "7/8",
                   "free", "irrational"}
# Vocal range
VOCAL_RANGES = {"soprano", "mezzo", "alto", "countertenor", "tenor",
                "baritone", "bass", "instrumental"}
# Lyric language
LYRIC_LANGUAGES = {"none", "english", "latin", "german", "french", "italian",
                    "spanish", "sanskrit", "hebrew", "arabic", "japanese",
                    "chinese", "portuguese", "yiddish", "gaelic", "old_english"}
# Lyric register
LYRIC_REGISTERS = {"narrative", "lyric", "dramatic", "didactic", "devotional",
                   "satiric", "erotic", "epic", "epigrammatic", "concrete",
                   "abstract", "incantatory"}
# Mix profiles
MIX_PROFILES = {"dry", "natural", "studio_warm", "studio_cold", "lo_fi",
                "hi_fi", "ambient_wash", "tape_saturation", "analog_summing",
                "digital_clean", "live", "multitrack"}
# Master targets (LUFS-ish)
MASTER_TARGETS = {"broadcast_-14", "spotify_-14", "apple_-16", "cd_-9",
                  "vinyl_-6", "lo_fi_unbounded", "live_unbounded"}
# Royalty mode
ROYALTY_MODES = {"public_domain", "cc0", "cc_by", "cc_by_sa", "arrangement",
                 "original"}
# Commit asset gate
COMMIT_ASSET = {"gate", "allow", "forbid"}


# ---------------------------------------------------------------------------
# Track (the canonical record)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Track:
    """A music track — frozen record of axes per AGENTS.md."""

    # identity / lineage
    track_id: str
    variant_of: str
    source_id: str  # every track traces back to a pd source

    # Group A — identity (genre, bpm, key, mode, time-sig, length)
    genre: str
    bpm: int
    key: str
    mode: str
    time_signature: str
    length_target_sec: float
    tempo_bucket: str

    # Group B — sound (vocal, instruments, mix, master)
    vocal_range: str
    instrument_set: Tuple[str, ...]
    mix_profile: str
    master_target: str

    # Group C — lyric (language, register, banned terms)
    lyric_language: str
    lyric_register: str
    banned_terms: Tuple[str, ...]

    # Group D — lineage (royalty + source discipline)
    royalty_mode: str
    source_discipline: str

    # Pipeline
    tool_id: str
    model_id: str
    generator_may_propose: bool
    commit_asset: str


# ---------------------------------------------------------------------------
# Compile (the canonical form for hashing)
# ---------------------------------------------------------------------------

def _canonical(axes: Dict[str, Any]) -> str:
    """Return a canonical JSON string for hashing.

    Derived identity fields (track_id) are stripped before hashing.
    """
    derived = {"track_id"}
    filtered = {k: v for k, v in axes.items() if k not in derived}

    def norm(v):
        if isinstance(v, (list, tuple)):
            return sorted([norm(x) for x in v if x is not None])
        if isinstance(v, dict):
            return {k: norm(val) for k, val in sorted(v.items())}
        if v is None:
            return None
        return v

    return json.dumps(norm(filtered), sort_keys=True, separators=(",", ":"))


def _tempo_bucket(bpm: int) -> str:
    if bpm < 40: return "grave"
    if bpm < 60: return "largo"
    if bpm < 70: return "adagio"
    if bpm < 80: return "andante"
    if bpm < 100: return "moderato"
    if bpm < 120: return "allegretto"
    if bpm < 140: return "allegro"
    if bpm < 180: return "presto"
    return "prestissimo"


def compile_track(axes: Dict[str, Any]) -> Track:
    """Compile a dict of track axes into a frozen Track.

    The track_id is sha256(canonical(axes)) truncated to 16 hex chars.
    """
    canonical = _canonical(axes)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

    # Validate enums
    for k, vs, label in [
        ("genre", GENRES, "Identity"),
        ("key", KEYS, "Identity"),
        ("mode", MODES, "Identity"),
        ("time_signature", TIME_SIGNATURES, "Identity"),
        ("vocal_range", VOCAL_RANGES, "Sound"),
        ("mix_profile", MIX_PROFILES, "Sound"),
        ("master_target", MASTER_TARGETS, "Sound"),
        ("lyric_language", LYRIC_LANGUAGES, "Lyric"),
        ("lyric_register", LYRIC_REGISTERS, "Lyric"),
        ("royalty_mode", ROYALTY_MODES, "Lineage"),
        ("commit_asset", COMMIT_ASSET, "Pipeline"),
    ]:
        v = axes.get(k)
        if v is not None and v not in vs:
            raise ValueError(f"{label} axis {k!r}={v!r} not in {sorted(vs)}")

    bpm = int(axes.get("bpm", 120))
    tempo = axes.get("tempo_bucket", _tempo_bucket(bpm))
    if tempo not in TEMPO_BUCKETS:
        raise ValueError(f"Identity axis 'tempo_bucket'={tempo!r} not in {sorted(TEMPO_BUCKETS)}")

    return Track(
        track_id=digest,
        variant_of=axes.get("variant_of", ""),
        source_id=axes.get("source_id", ""),
        genre=axes.get("genre", "classical"),
        bpm=bpm,
        key=axes.get("key", "C"),
        mode=axes.get("mode", "major"),
        time_signature=axes.get("time_signature", "4/4"),
        length_target_sec=float(axes.get("length_target_sec", 180.0)),
        tempo_bucket=tempo,
        vocal_range=axes.get("vocal_range", "instrumental"),
        instrument_set=tuple(axes.get("instrument_set", [])),
        mix_profile=axes.get("mix_profile", "natural"),
        master_target=axes.get("master_target", "broadcast_-14"),
        lyric_language=axes.get("lyric_language", "none"),
        lyric_register=axes.get("lyric_register", "narrative"),
        banned_terms=tuple(axes.get("banned_terms", [])),
        royalty_mode=axes.get("royalty_mode", "public_domain"),
        source_discipline=axes.get("source_discipline", ""),
        tool_id=axes.get("tool_id", ""),
        model_id=axes.get("model_id", ""),
        generator_may_propose=bool(axes.get("generator_may_propose", False)),
        commit_asset=axes.get("commit_asset", "gate"),
    )


# ---------------------------------------------------------------------------
# Gate (the single commit_asset checker)
# ---------------------------------------------------------------------------

def gate(track: Optional[Track], asset_text: str = "") -> Tuple[bool, str]:
    """Check the gate. Returns (allow, reason)."""

    if track is None:
        return False, "no_track"

    if track.commit_asset == "forbid":
        return False, "commit_forbidden"

    if track.commit_asset == "allow":
        return True, "ok"

    # commit_asset == "gate" (default)
    if not track.track_id:
        return False, "no_track_id"

    if not track.source_id:
        # every track traces back to a pd source
        return False, "no_source_id"

    if track.royalty_mode not in ("public_domain", "cc0", "cc_by",
                                   "cc_by_sa", "arrangement", "original"):
        return False, f"royalty_mode_invalid:{track.royalty_mode}"

    if track.banned_terms:
        text_lower = asset_text.lower()
        for term in track.banned_terms:
            if term.lower() in text_lower:
                return False, f"banned_term:{term}"

    return True, "ok"


# ---------------------------------------------------------------------------
# to_dict (for serialization to YAML / JSON)
# ---------------------------------------------------------------------------

def track_to_dict(track: Track) -> Dict[str, Any]:
    """Return a plain dict from a Track."""
    d = asdict(track)
    return {k: list(v) if isinstance(v, tuple) else v for k, v in d.items()}


__all__ = [
    "Track",
    "compile_track",
    "gate",
    "track_to_dict",
    # enums
    "TEMPO_BUCKETS", "GENRES", "KEYS", "MODES", "TIME_SIGNATURES",
    "VOCAL_RANGES", "LYRIC_LANGUAGES", "LYRIC_REGISTERS",
    "MIX_PROFILES", "MASTER_TARGETS", "ROYALTY_MODES", "COMMIT_ASSET",
]