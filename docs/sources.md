# sources — public-domain music corpora

Public-domain sources far-music draws from for the `source_id` axis
(AGENTS.md). Every track must trace back to a pd source or carry an
explicit `royalty_mode` in `{cc0, cc_by, cc_by_sa, arrangement, original}`.

## primary sources

### imslp — international music score library project
- **url:** https://imslp.org/
- **license:** pd for composers who died >100 years ago (varies by country)
- **what we get:** classical scores (Bach, Mozart, Schubert, Beethoven,
  Brahms, Chopin, etc.)
- **notes:** the canonical pd classical source. verify per-work license.

### mutopiaproject — classical sheet music + midi
- **url:** https://www.mutopiaproject.org/
- **license:** pd (CC0 or public domain dedication)
- **what we get:** typeset scores + midi files for classical works
- **notes:** smaller collection than imslp but more uniformly pd.

### freesound CC0 — sound effects + samples
- **url:** https://freesound.org/browse/tags/cc0/
- **license:** CC0
- **what we get:** one-shots, foley, loops, stems
- **notes:** filter by tag `cc0` for license-clean content.

### freesound CC-BY — same with attribution
- **url:** https://freesound.org/
- **license:** CC-BY, CC-BY-SA, etc.
- **what we get:** wider selection
- **notes:** carry attribution in track metadata.

### wikimedia commons audio
- **url:** https://commons.wikimedia.org/wiki/Category:Audio
- **license:** varies; pd + CC0 dominate
- **what we get:** folk music, historical recordings, sound logos

### komplete commons (Native Instruments)
- **url:** https://www.native-instruments.com/en/products/komplete/komplete-commons/
- **license:** royalty-free for use in productions (not reselling the samples)
- **what we get:** production-grade samples, loops, presets
- **notes:** great for stems. check the EULA carefully.

## secondary sources

- **public domain review:** curated essays + audio
- **archive.org audio:** open-source audio archive
- **loc.gov national recording preservation:** historic US recordings

## how to add a new source

1. Add the entry under "primary" or "secondary"
3. Add a test verifying the gate behavior

## See also

- [AGENTS.md](../AGENTS.md) — the contract
- [tools/track.py](../tools/track.py) — compile + gate