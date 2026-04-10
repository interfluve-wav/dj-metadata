---
tags: [udms, schema, dj-metadata, python, rekordbox, serato, traktor]
created: 2026-04-10
related:
  - "[[Paper Draft]]"
  - "[[Experiments Overview]]"
  - "[[ML-AI-Intersection - New References]]"
---

# UDMS Schema Reference

**File**: `code/schema/udms_schema.py`
**Repo**: [github.com/interfluve-wav/dj-metadata-paper](https://github.com/interfluve-wav/dj-metadata-paper)
**Status**: Reference implementation complete

## Schema Overview

UDMS (Unified DJ Metadata Schema) defines 18 canonical fields. Dashes = no native equivalent; field dropped in that direction.

| Field | Type | Rekordbox | Serato | Traktor |
|---|---|---|---|---|
| title | string | TrackName | title | Title |
| artist | string | Artist | artist | Artist |
| album | string | Album | album | Album |
| genre | string | Genre | genre | Genre |
| bpm | float | AverageBpm | bpm | BPM |
| key | string | Tonality | key | Key |
| key_numeric | int [0–11] | — | — | Key_ID |
| rating | int [0–5] | RatingByte | rating | Rating |
| energy | int [1–10] | Energy | — | — |
| mood | int [1–10] | Mood | — | — |
| label | string | Label | label | Label |
| catalog_no | string | CatalogNo | — | — |
| duration_sec | int | TotalTime | length | Length_ms |
| bitrate | int | BitRate | bit_rate | Bitrate |
| sample_rate | int | SampleRate | sample_rate | SampleRate |
| file_path | string | Location | path | Location |
| playlist_name | string | PlaylistName | crate_name | CollectionEntry |

## Key Normalization

UDMS adopts **Camelot notation** as canonical. Three native formats are normalized:

```
Traditional (e.g., "C major") → Camelot via TRADITIONAL_TO_CAMELOT dict
OpenKey (e.g., "1d") → Camelot via OPENKEY_MAP dict  
Numeric (Traktor Key_ID 0–11) → OpenKey order → Camelot
```

### Camelot Mapping Table

Major keys: 8B→C, 9B→G, 10B→D, 11B→A, 12B→E, 1B→B, 2B→F#/Gb, 3B→C#/Db, 7B→F, 6B→Bb, 3B→Eb, 4B→Ab, 5B→Db, 6B→Gb
Minor keys: 8A→A, 9A→E, 10A→B, 11A→F#, 12A→C#, 1A→G#, 2A→D#/Eb, 7A→D, 6A→G, 3A→C, 4A→F, 5A→Bb, 2A→Eb

## Rating Normalization

Rekordbox stores rating as 0–255 (RatingByte); UDMS normalizes to 0–5:
```python
udms.rating = round(val / 51)  # 255/5 = 51
```

Serato and Traktor store native 0–5 scales, used directly.

## Platform Adapters

Three adapters implement `to_udms()`:
- `RekordboxAdapter` → uses `REKORDBOX_FIELDS` map
- `SeratoAdapter` → uses `SERATO_FIELDS` map
- `TraktorAdapter` → uses `TRAKTOR_FIELDS` map

All inherit from `PlatformAdapter` base class.

## Preservation Metrics

```python
def preservation_rate(original: UDMS, transferred: UDMS, field: str) -> float
def aggregate_quality_score(original: UDMS, transferred: UDMS, fields: list[str]) -> float
```

BPM tolerance: ±0.001 for float comparison.

## Usage

```python
from udms_schema import transfer_with_udms, Platform, ADAPTERS

udms_track = transfer_with_udms(track_dict, Platform.REKORDBOX)
print(udms_track.to_dict())
```

## Design Principles

1. **Least common denominator** — only fields all 3 platforms support become UDMS canonicals
2. **Expressive sufficiency** — all DJ-relevant metadata fields captured
3. **Lossless round-tripping** — p → q → p cycles preserve values

## Open Implementation Items

- [ ] Complete Serato → UDMS adapter (handle crate_ fields)
- [ ] Complete Traktor → UDMS adapter (handle collection entry format)
- [ ] Add JSON Schema for machine-readable UDMS validation
