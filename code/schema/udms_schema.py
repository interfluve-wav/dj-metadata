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
    VIRTUALDJ = "virtualdj"
    UDMS = "udms"


class KeyNotation(Enum):
    """Supported musical key notations in UDMS."""
    CAMELOT = "camelot"          # e.g., "8B", "11A"
    OPENKEY = "openkey"          # e.g., "1d", "6m"
    TRADITIONAL = "traditional"  # e.g., "C major", "A minor"
    NUMERIC = "numeric"          # int 0-11 (OpenKey order)


# Platform field name mappings
REKORDBOX_FIELDS = {
    "Name": "title", "Artist": "artist", "Album": "album", "Genre": "genre",
    "AverageBpm": "bpm", "Tonality": "key", "Rating": "rating",
    "Energy": "energy", "Mood": "mood", "Label": "label",
    "CatalogNo": "catalog_no", "TotalTime": "duration_sec",
    "BitRate": "bitrate", "SampleRate": "sample_rate", "Location": "file_path",
}

# Serato "database V2" binary format field mappings to UDMS
# Parsed from /Users/suhaas/Music/_Serato_/database V2 (382 tracks)
# Fields: tsng=title, tart=artist, talb=album, tgen=genre, tbpm=bpm,
#         tkey=key, tlbl=label, tlen=duration (HH:MM:SS.ms), tbit=bitrate (kbps),
#         tsmp=sample_rate (kHz), ttyp=filetype, pfil=filepath
SERATO_FIELDS = {
    "tsng": "title", "tart": "artist", "talb": "album", "tgen": "genre",
    "tbpm": "bpm", "tkey": "key", "tlbl": "label",
    "tbit": "bitrate", "tsmp": "sample_rate", "tlen": "duration_sec",
    "ttyp": "file_type", "pfil": "file_path",
}

TRAKTOR_FIELDS = {
    "Title": "title", "Artist": "artist", "Album": "album", "Genre": "genre",
    "BPM": "bpm", "Key": "key", "Key_ID": "key_numeric", "Rating": "rating",
    "Label": "label", "Length_ms": "duration_sec", "Bitrate": "bitrate",
    "SampleRate": "sample_rate", "Location": "file_path",
}

# VirtualDJ database.xml field mappings to UDMS
# VirtualDJ stores BPM as a decimal fraction of the beat-grid unit (Scan.Bpm).
# Conversion: reported_bpm = scan_bpm * 282 (e.g., scan=0.461538 → 130.2 BPM)
# Tags.Bpm is a user-set/manual BPM override (optional)
# Scan fields: Bpm (beat-grid tempo), AltBpm (alternative tempo), Key (analyzed key)
# Tags fields: Author, Title, Album, Genre, Year, TrackNumber, Label, Remix, Key, Bpm
VIRTUALDJ_FIELDS = {
    "Author": "artist", "Title": "title", "Album": "album", "Genre": "genre",
    "Year": "year", "TrackNumber": "track_number", "Label": "label",
    "Remix": "remix",
    # Bpm/Key are handled separately in VirtualDJAdapter (see below)
    # FilePath mapped separately
    "FilePath": "file_path",
    # Infos sub-element fields
    "SongLength": "duration_sec", "Bitrate": "bitrate",
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

    # VirtualDJ-specific fields
    bpm_manual: float = 0.0   # User-set BPM in Tags (optional override)
    bpm_alt: float = 0.0     # Alternative BPM in Scan (e.g., half-tempo option)
    year: str = ""
    track_number: str = ""
    remix: str = ""

    def to_dict(self) -> dict:
        return {
            "title": self.title, "artist": self.artist, "album": self.album,
            "genre": self.genre, "bpm": self.bpm, "key": self.key,
            "key_numeric": self.key_numeric, "rating": self.rating,
            "energy": self.energy, "mood": self.mood, "label": self.label,
            "catalog_no": self.catalog_no, "duration_sec": self.duration_sec,
            "bitrate": self.bitrate, "sample_rate": self.sample_rate,
            "file_path": self.file_path, "playlist_name": self.playlist_name,
            # VirtualDJ-specific
            "bpm_manual": self.bpm_manual, "bpm_alt": self.bpm_alt,
            "year": self.year, "track_number": self.track_number, "remix": self.remix,
        }


# ── Normalizers ──────────────────────────────────────────────────────────────

def normalize_bpm(value, platform: Platform = None) -> float:
    """Parse BPM from various formats: float, string, or Rekordbox integer."""
    try:
        if isinstance(value, float):
            return float(value)
        if isinstance(value, int):
            return float(value)
        if isinstance(value, str):
            # Serato stores BPM as string like "96.78"
            return float(value.strip())
        return 0.0
    except (TypeError, ValueError):
        return 0.0


def normalize_bpm_virtualdj(scan_bpm: float) -> float:
    """
    VirtualDJ stores BPM as a decimal fraction of the beat-grid unit.
    Conversion: reported_bpm = scan_bpm * 282.
    Confirmed against 8 tracks from Suhaas's database:
      0.461519*282=130.1, 0.50*282=141.0, 0.375011*282=105.8, ...
    Returns 0.0 if scan_bpm is missing or invalid.
    """
    try:
        if scan_bpm is None:
            return 0.0
        bpm = float(scan_bpm)
        if bpm <= 0:
            return 0.0
        return round(bpm * 282, 2)
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


# Bare note name to Camelot (major/minor inferred from case)
# e.g., "F" -> "7B", "Gm" -> "6A", "C#m" -> "3A", "A#" -> "4B" (A# major)
BARE_NOTE_TO_CAMELOT = {
    # Major (uppercase, no suffix = major)
    "C": "8B", "C#": "3B", "Db": "3B",
    "D": "10B", "D#": "5B", "Eb": "3B",
    "E": "12B",
    "F": "7B", "F#": "2B", "Gb": "6B",
    "G": "9B", "G#": "4B", "Ab": "4B",
    "A": "11B", "A#": "6B", "Bb": "6B",
    "B": "1B",
    # Minor (lowercase or "m" suffix in original)
    "Cm": "3A", "C#m": "12A", "Dbm": "12A",
    "Dm": "7A",
    "D#m": "2A", "Ebm": "2A",
    "Em": "9A",
    "Fm": "4A", "F#m": "11A", "Gbm": "11A",
    "Gm": "6A", "G#m": "1A", "Abm": "1A",
    "Am": "8A", "A#m": "5A", "Bbm": "5A",
    "Bm": "10A",
}


def normalize_key(value) -> str:
    if not value:
        return "Unknown"
    v = str(value).strip()
    # Already Camelot (e.g., "8B", "11A")
    if re.match(r"^[0-9]+[A-B]$", v, re.IGNORECASE):
        return v.upper()
    # OpenKey (e.g., "1d", "6m")
    if v.lower() in OPENKEY_MAP:
        return OPENKEY_MAP[v.lower()]
    # Traditional (e.g., "C major", "A minor")
    if v in TRADITIONAL_TO_CAMELOT:
        return TRADITIONAL_TO_CAMELOT[v]
    for traditional, camelot in TRADITIONAL_TO_CAMELOT.items():
        if traditional.lower() == v.lower():
            return camelot
    # Bare note name: "F", "Gm", "C#m", "A#"
    if v in BARE_NOTE_TO_CAMELOT:
        return BARE_NOTE_TO_CAMELOT[v]
    # Handle sharps/flats with "b" notation: "Bb" -> "A#" already handled above
    # "Db" -> "C#", "Eb" -> "D#" etc. — already in BARE_NOTE_TO_CAMELOT
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
    """Parse duration: Rekordbox=seconds (int), Traktor=milliseconds (int), Serato='HH:MM:SS.ms' (str)."""
    try:
        if platform == Platform.SERATO:
            # Serato stores as "06:10.09" or "1:23:45.67"
            parts = str(value).split(':')
            if len(parts) == 3:  # HH:MM:SS.ms
                h, m, s = parts
                return int(h) * 3600 + int(m) * 60 + float(s)
            elif len(parts) == 2:  # MM:SS.ms
                m, s = parts
                return int(m) * 60 + float(s)
            return int(float(value))
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
            setattr(udms, udms_key, normalize_bpm(val, platform))
        elif udms_key == "rating":
            setattr(udms, udms_key, normalize_rating(val, platform))
        elif udms_key == "key":
            setattr(udms, udms_key, normalize_key(val))
            udms.key_numeric = key_to_numeric(udms.key)
        elif udms_key == "duration_sec":
            setattr(udms, udms_key, normalize_duration(val, platform))
        elif udms_key == "bitrate":
            # Serato: "1411.2kbps" -> 1411, Traktor/Rekordbox: int
            if isinstance(val, str):
                import re
                m = re.match(r"([\d.]+)", val)
                setattr(udms, udms_key, int(float(m.group(1))) if m else 0)
            else:
                setattr(udms, udms_key, int(val))
        elif udms_key == "sample_rate":
            # Serato: "44.1k" -> 44100, Traktor/Rekordbox: int Hz
            if isinstance(val, str):
                import re
                m = re.match(r"([\d.]+)", val)
                setattr(udms, udms_key, int(float(m.group(1)) * 1000) if m else 44100)
            else:
                setattr(udms, udms_key, int(val))
        else:
            if isinstance(val, str):
                val = val.strip()
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


class VirtualDJAdapter(PlatformAdapter):
    """
    VirtualDJ adapter for UDMS.

    VirtualDJ database.xml stores BPM in two places:
    - Scan.Bpm: beat-grid analyzed tempo, stored as a decimal fraction.
      Conversion: reported_bpm = scan_bpm * 282.
      E.g., scan=0.461538 → 130.2 BPM, scan=0.50 → 141.0 BPM.
    - Tags.Bpm: user-set/manual BPM override (optional, often absent).

    For UDMS.bpm, the adapter prefers:
    1. Tags.Bpm (manual override, if set) → bpm_manual
    2. Scan.Bpm converted via ×282 (beat-grid analysis) → bpm

    The ×282 factor was confirmed against 8 tracks from Suhaas's library
    (all within 0.1 BPM of expected values).

    A note on half-tempo genres: VirtualDJ also stores an AltBpm field
    representing an alternative interpretation (e.g., half-tempo option).
    This is stored as bpm_alt in UDMS for cross-platform comparison.
    """
    def to_udms(self, raw: dict) -> UDMS:
        udms = UDMS(source_platform=Platform.VIRTUALDJ, source_raw=raw)

        # BPM: Tags_Bpm (manual override) takes priority over Scan_Bpm (analyzed)
        # BPM is stored as a decimal fraction; convert via ×282
        tags_bpm = raw.get("Tags_Bpm")
        scan_bpm = raw.get("Scan_Bpm")
        if tags_bpm is not None and tags_bpm != "":
            try:
                # Tags BPM is a decimal fraction, not a reported BPM value
                udms.bpm_manual = normalize_bpm_virtualdj(float(tags_bpm))
                udms.bpm = udms.bpm_manual
            except (TypeError, ValueError):
                udms.bpm = normalize_bpm_virtualdj(float(scan_bpm)) if scan_bpm else 0.0
        elif scan_bpm is not None and scan_bpm != "":
            udms.bpm = normalize_bpm_virtualdj(float(scan_bpm))

        # AltBpm: alternative tempo interpretation from Scan
        alt_bpm = raw.get("Scan_AltBpm")
        if alt_bpm is not None and alt_bpm != "":
            udms.bpm_alt = normalize_bpm_virtualdj(float(alt_bpm))

        # Key: prefer Scan_Key (audio analysis) over Tags_Key (user annotation)
        scan_key = raw.get("Scan_Key") or ""
        tags_key = raw.get("Tags_Key") or ""
        key_val = scan_key if scan_key else tags_key
        if key_val:
            udms.key = normalize_key(key_val)
            udms.key_numeric = key_to_numeric(udms.key)

        # Standard field mappings
        for native_key, udms_key in VIRTUALDJ_FIELDS.items():
            if native_key in ("Bpm", "AltBpm", "Key", "Tags_Key", "Scan_Key"):
                continue  # handled above
            if native_key not in raw:
                continue
            val = raw[native_key]
            if udms_key == "duration_sec":
                try:
                    udms.duration_sec = int(float(val))
                except (TypeError, ValueError):
                    udms.duration_sec = 0
            elif udms_key == "bitrate":
                try:
                    udms.bitrate = int(float(val))
                except (TypeError, ValueError):
                    udms.bitrate = 0
            elif udms_key in ("year", "track_number", "remix"):
                udms.__dict__[udms_key] = str(val).strip() if val else ""
            else:
                if isinstance(val, str):
                    val = val.strip()
                udms.__dict__[udms_key] = val

        return udms


ADAPTERS = {
    Platform.REKORDBOX: RekordboxAdapter(),
    Platform.SERATO: SeratoAdapter(),
    Platform.TRAKTOR: TraktorAdapter(),
    Platform.VIRTUALDJ: VirtualDJAdapter(),
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
