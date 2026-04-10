"""
UDMS — Unified DJ Metadata Schema
A canonical metadata schema for cross-platform DJ library interoperability.

Reference implementation: https://github.com/interfluve-wav/dj-metadata-paper
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import re


class Platform(Enum):
    REKORDBOX = "rekordbox"
    SERATO = "serato"
    TRAKTOR = "traktor"
    UDMS = "udms"


class KeyNotation(Enum):
    """Supported musical key notations in UDMS."""
    CAMELOT = "camelot"          # e.g., "8B", "11A"
    OPENKEY = "openkey"          # e.g., "1d", "6m"
    TRADITIONAL = "traditional"  # e.g., "C major", "A minor"
    NUMERIC = "numeric"          # int 0-11 (OpenKey order)


# Platform field name mappings
REKORDBOX_FIELDS = {
    "TrackName": "title", "Artist": "artist", "Album": "album", "Genre": "genre",
    "AverageBpm": "bpm", "Tonality": "key", "RatingByte": "rating",
    "Energy": "energy", "Mood": "mood", "Label": "label",
    "CatalogNo": "catalog_no", "TotalTime": "duration_sec",
    "BitRate": "bitrate", "SampleRate": "sample_rate", "Location": "file_path",
}

SERATO_FIELDS = {
    "title": "title", "artist": "artist", "album": "album", "genre": "genre",
    "bpm": "bpm", "key": "key", "rating": "rating", "label": "label",
    "length": "duration_sec", "bit_rate": "bitrate", "sample_rate": "sample_rate",
    "path": "file_path",
}

TRAKTOR_FIELDS = {
    "Title": "title", "Artist": "artist", "Album": "album", "Genre": "genre",
    "BPM": "bpm", "Key": "key", "Key_ID": "key_numeric", "Rating": "rating",
    "Label": "label", "Length_ms": "duration_sec", "Bitrate": "bitrate",
    "SampleRate": "sample_rate", "Location": "file_path",
}


@dataclass
class UDMS:
    """Unified DJ Metadata Schema — canonical track representation."""
    title: str = ""
    artist: str = ""
    album: str = ""
    genre: str = ""
    bpm: float = 0.0
    key: str = ""            # Canonical: Camelot notation (e.g., "8B")
    key_numeric: int = -1    # Numeric fallback: 0-11 (OpenKey order)
    rating: int = 0          # 0-5 scale
    energy: int = 0          # 1-10
    mood: int = 0            # 1-10
    label: str = ""
    catalog_no: str = ""
    duration_sec: int = 0
    bitrate: int = 0
    sample_rate: int = 44100
    file_path: str = ""
    playlist_name: str = ""
    source_platform: Optional[Platform] = None
    source_raw: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "title": self.title, "artist": self.artist, "album": self.album,
            "genre": self.genre, "bpm": self.bpm, "key": self.key,
            "key_numeric": self.key_numeric, "rating": self.rating,
            "energy": self.energy, "mood": self.mood, "label": self.label,
            "catalog_no": self.catalog_no, "duration_sec": self.duration_sec,
            "bitrate": self.bitrate, "sample_rate": self.sample_rate,
            "file_path": self.file_path, "playlist_name": self.playlist_name,
        }


# ── Normalizers ──────────────────────────────────────────────────────────────

def normalize_bpm(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def normalize_rating(value, platform: Platform) -> int:
    try:
        val = int(value)
        if platform == Platform.REKORDBOX:
            return round(val / 51)  # 255/5 = 51
        return max(0, min(5, val))
    except (TypeError, ValueError):
        return 0


TRADITIONAL_TO_CAMELOT = {
    "C major": "8B", "G major": "9B", "D major": "10B", "A major": "11B",
    "E major": "12B", "B major": "1B", "F# major": "2B", "C# major": "3B",
    "F major": "7B", "Bb major": "6B", "Eb major": "3B", "Ab major": "4B",
    "Db major": "5B", "Gb major": "6B", "A minor": "8A", "E minor": "9A",
    "B minor": "10A", "F# minor": "11A", "C# minor": "12A", "G# minor": "1A",
    "D# minor": "2A", "D minor": "7A", "G minor": "6A", "C minor": "3A",
    "F minor": "4A", "Bb minor": "5A", "Eb minor": "2A",
}

OPENKEY_MAP = {
    "1d": "8B", "2d": "9B", "3d": "10B", "4d": "11B", "5d": "12B",
    "6d": "1B", "7d": "2B", "8d": "3B", "9d": "4B", "10d": "5B",
    "11d": "6B", "12d": "7B", "1m": "8A", "2m": "9A", "3m": "10A",
    "4m": "11A", "5m": "12A", "6m": "1A", "7m": "2A", "8m": "3A",
    "9m": "4A", "10m": "5A", "11m": "6A", "12m": "7A",
}


def normalize_key(value) -> str:
    if not value:
        return "Unknown"
    v = str(value).strip()
    if re.match(r"^[0-9]+[A-B]$", v, re.IGNORECASE):
        return v.upper()
    if v.lower() in OPENKEY_MAP:
        return OPENKEY_MAP[v.lower()]
    if v in TRADITIONAL_TO_CAMELOT:
        return TRADITIONAL_TO_CAMELOT[v]
    for traditional, camelot in TRADITIONAL_TO_CAMELOT.items():
        if traditional.lower() == v.lower():
            return camelot
    return "Unknown"


def key_to_numeric(key_camelot: str) -> int:
    if key_camelot == "Unknown":
        return -1
    try:
        num = int(re.match(r"([0-9]+)", key_camelot).group(1))
        letter = key_camelot[-1].upper()
        return (num - 1) + (0 if letter == "B" else 12)
    except (ValueError, AttributeError):
        return -1


def normalize_duration(value, platform: Platform) -> int:
    try:
        val = float(value)
        return int(val / 1000) if platform == Platform.TRAKTOR else int(val)
    except (TypeError, ValueError):
        return 0


# ── Platform Adapters ────────────────────────────────────────────────────────

class PlatformAdapter:
    def to_udms(self, raw: dict) -> UDMS:
        raise NotImplementedError


def _apply_normalization(udms: UDMS, raw: dict, field_map: dict, platform: Platform) -> UDMS:
    for native_key, udms_key in field_map.items():
        if native_key not in raw:
            continue
        val = raw[native_key]
        if udms_key == "bpm":
            setattr(udms, udms_key, normalize_bpm(val))
        elif udms_key == "rating":
            setattr(udms, udms_key, normalize_rating(val, platform))
        elif udms_key == "key":
            setattr(udms, udms_key, normalize_key(val))
            udms.key_numeric = key_to_numeric(udms.key)
        elif udms_key == "duration_sec":
            setattr(udms, udms_key, normalize_duration(val, platform))
        else:
            setattr(udms, udms_key, val)
    return udms


class RekordboxAdapter(PlatformAdapter):
    def to_udms(self, raw: dict) -> UDMS:
        udms = UDMS(source_platform=Platform.REKORDBOX, source_raw=raw)
        return _apply_normalization(udms, raw, REKORDBOX_FIELDS, Platform.REKORDBOX)


class SeratoAdapter(PlatformAdapter):
    def to_udms(self, raw: dict) -> UDMS:
        udms = UDMS(source_platform=Platform.SERATO, source_raw=raw)
        return _apply_normalization(udms, raw, SERATO_FIELDS, Platform.SERATO)


class TraktorAdapter(PlatformAdapter):
    def to_udms(self, raw: dict) -> UDMS:
        udms = UDMS(source_platform=Platform.TRAKTOR, source_raw=raw)
        return _apply_normalization(udms, raw, TRAKTOR_FIELDS, Platform.TRAKTOR)


ADAPTERS = {
    Platform.REKORDBOX: RekordboxAdapter(),
    Platform.SERATO: SeratoAdapter(),
    Platform.TRAKTOR: TraktorAdapter(),
}


def transfer_with_udms(track: dict, from_platform: Platform) -> UDMS:
    adapter = ADAPTERS.get(from_platform)
    if not adapter:
        raise ValueError(f"Unknown platform: {from_platform}")
    return adapter.to_udms(track)


# ── Preservation Metrics ──────────────────────────────────────────────────────

def preservation_rate(original: UDMS, transferred: UDMS, field: str) -> float:
    orig_val = getattr(original, field, None)
    trans_val = getattr(transferred, field, None)
    if orig_val == trans_val:
        return 1.0
    if orig_val is None or trans_val is None:
        return 0.0
    if isinstance(orig_val, float) and isinstance(trans_val, float):
        return 1.0 if abs(orig_val - trans_val) < 0.001 else 0.0
    return 0.0


def aggregate_quality_score(original: UDMS, transferred: UDMS, fields: list[str]) -> float:
    rates = [preservation_rate(original, transferred, f) for f in fields]
    return sum(rates) / len(rates) if rates else 0.0
