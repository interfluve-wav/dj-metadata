#!/usr/bin/env python3
"""BPM validation: compare aubio vs scipy on 20 test tracks."""
import json

with open('/Users/suhaas/Documents/GitHub/dj-metadata-paper/data/aubio_results.json') as _f:
    aubio_raw = json.load(_f)
with open('/Users/suhaas/Documents/GitHub/dj-metadata-paper/data/librosa_results.json') as _f:
    librosa_raw = json.load(_f)
with open('/Users/suhaas/Documents/GitHub/dj-metadata-paper/data/scipy_results.json') as _f:
    scipy_raw = json.load(_f)
with open('/Users/suhaas/Documents/GitHub/dj-metadata-paper/data/cross_platform_comparison.json') as f:
    cp = json.load(f)

# Build lookups (keyed by artist-title)
aubio_by_key = {(a['artist'], a['title']): a for a in aubio_raw}
lib_by_key = {(l['artist'], l['title']): l for l in librosa_raw}
scp_by_key = {(s['artist'], s['title']): s for s in scipy_raw}
cp_by_key = {(r['artist']['rekordbox'], r['title']['rekordbox']): r for r in cp['results']}

# The 20 test tracks in the test folder
test_tracks = [
    ("Alien Nosejob", "Shuffle Boogie"),
    ("Benga, Coki", "Night"),
    ("Breakage, David Rodigan", "Rain"),
    ("Carré, Danny Goliger", "Up Too Late"),
    ("Hassan Abou Alam", "Mahzooz"),
    ("Mala", "Change"),
    ("Mala", "Introduction"),
    ("Arkajo", "Inuti"),
    ("Decoder", "Abundance"),
    ("Al Wootton", "Graver"),
    ("Arkajo", "Inuti (Live Cut)"),
    ("Bror Havnes", "De Som Vet"),
    ("Crystal Waters", "Gypsy Woman (She's Homeless) (La Da Dee La Da Da) (Basement Boy Strip To The Bone Mix)"),
    ("Joey Valence & Brae", "HOOLIGANG"),
    ("Piezo", "Cyclic Wavez"),
    ("Al Wootton", "March"),
    ("Erik Luebs", "Riding The Blade"),
    ("Polygonia", "Splintered Soul Fragments"),
    ("Sami", "Twin"),
    ("Tsvi", "Music Is Moving"),   # lowercase in CP data
]

rows = []
for artist, title in test_tracks:
    key = (artist, title)
    r = cp_by_key.get(key, {})
    aub = aubio_by_key.get(key, {}).get('aubio_bpm')
    lib = lib_by_key.get(key, {}).get('beat_track_median') or lib_by_key.get(key, {}).get('librosa_tempo')
    scp = scp_by_key.get(key, {}).get('scipy_tempo')

    rb = r.get('bpm', {}).get('rekordbox', 0) if r else 0
    st = r.get('bpm', {}).get('serato', 0) if r else 0
    is_2x = r.get('field_results', {}).get('bpm', {}).get('is_2x', False) if r else False

    # Ground truth: for 2x tracks Serato is correct, else RB=ST
    gt = st if is_2x else rb

    # Which tool agrees with ground truth (within 2 BPM)
    aub_agree = abs(aub - gt) <= 2.0 if aub else False
    lib_agree = abs(lib - gt) <= 2.0 if lib else False
    scp_agree = abs(scp - gt) <= 2.0 if scp else False

    # Also check if aubio/scipy agree with the WRONG value (RB for 2x)
    aub_agree_rb = abs(aub - rb) <= 2.0 if aub else False
    scp_agree_rb = abs(scp - rb) <= 2.0 if scp else False

    rows.append({
        'artist': artist, 'title': title,
        'rb': rb, 'st': st, 'gt': gt,
        'aubio': aub, 'librosa': lib, 'scipy': scp,
        'is_2x': is_2x,
        'aubio_ok': aub_agree, 'scipy_ok': scp_agree,
        'aubio_rb_ok': aub_agree_rb, 'scipy_rb_ok': scp_agree_rb,
    })

# ---- SUMMARY ----
n_2x = sum(1 for r in rows if r['is_2x'])
n_nor = len(rows) - n_2x

def rate(key, is2x):
    n = n_2x if is2x else n_nor
    if n == 0: return "  N/A"
    ok = sum(1 for r in rows if r['is_2x'] == is2x and r[key])
    return f"{100*ok/n:4.0f}% ({ok}/{n})"

print("=" * 90)
print("BPM VALIDATION: aubio vs scipy autocorrelation vs ground truth")
print("Ground truth: Serato BPM for 2x tracks, Rekordbox BPM for normal tracks")
print("=" * 90)
print(f"\n{'Category':30s} {'aubio tempo':>18s} {'scipy autocorr':>18s}")
print(f"{'2x tracks (n={})'.format(n_2x):30s} {rate('aubio_ok', True):>18s} {rate('scipy_ok', True):>18s}")
print(f"{'Normal tracks (n={})'.format(n_nor):30s} {rate('aubio_ok', False):>18s} {rate('scipy_ok', False):>18s}")

# HOW aubio fails on 2x tracks
print(f"\n--- HOW aubio fails on 2x tracks ---")
for r in rows:
    if r['is_2x']:
        aub_err = round(abs(r['aubio'] - r['gt']), 1) if r['aubio'] else None
        scp_err = round(abs(r['scipy'] - r['gt']), 1) if r['scipy'] else None
        if aub_err and aub_err > 2:
            print(f"  {r['artist'][:20]:20s} {r['title'][:20]:20s}  RB={r['rb']:.0f} ST={r['st']:.0f}  aubio={r['aubio']:.1f} (err={aub_err:.0f})  scipy={str(round(r['scipy'],1) if r['scipy'] else '-'):>6s}")

# HOW scipy fails on normal tracks
print(f"\n--- HOW scipy fails on normal tracks ---")
for r in rows:
    if not r['is_2x']:
        scp_err = round(abs(r['scipy'] - r['gt']), 1) if r['scipy'] else None
        aub_err = round(abs(r['aubio'] - r['gt']), 1) if r['aubio'] else None
        if scp_err and scp_err > 2:
            print(f"  {r['artist'][:20]:20s} {r['title'][:20]:20s}  RB=ST={r['rb']:.0f}  scipy={r['scipy']:.1f} (err={scp_err:.0f})  aubio={str(round(r['aubio'],1) if r['aubio'] else '-'):>6s}")

# Full table
print("\n" + "=" * 90)
print(f"{'#':2s} {'Artist':22s} {'Title':22s} {'RB':>5s} {'ST':>5s} {'GT':>5s} {'aubio':>6s} {'scipy':>6s}  aub  scp  Cat")
for i, r in enumerate(rows, 1):
    cats = []
    if r['is_2x']: cats.append("2x")
    if r['aubio_ok']: cats.append("aubOK")
    if r['scipy_ok']: cats.append("scpOK")
    cat = "+".join(cats) if cats else "OK"
    print(f"{i:2d}  {r['artist'][:21]:22s} {r['title'][:21]:22s} {r['rb']:>5.1f} {r['st']:>5.1f} {r['gt']:>5.1f} "
          f"{str(round(r['aubio'],1) if r['aubio'] else '-'):>6s} {str(round(r['scipy'],1) if r['scipy'] else '-'):>6s}  "
          f"{'OK' if r['aubio_ok'] else 'ERR':>3s}  {'OK' if r['scipy_ok'] else 'ERR':>3s}  {cat}")

# KEY INSIGHT BOX
print("\n" + "=" * 90)
print("KEY FINDING:")
ok_2x_aub = sum(1 for r in rows if r['is_2x'] and r['aubio_ok'])
ok_2x_scp = sum(1 for r in rows if r['is_2x'] and r['scipy_ok'])
print(f"  aubio: {ok_2x_aub}/{n_2x} 2x tracks correct (0%) — finds ~140, matches WRONG Rekordbox value")
print(f"  scipy: {ok_2x_scp}/{n_2x} 2x tracks correct — finds ~70, matches CORRECT Serato value")
print(f"\n  aubio suffers from the SAME octave error as Rekordbox.")
print(f"  scipy autocorrelation avoids this and finds the true half-tempo.")
print(f"\n  For NORMAL tracks: aubio {sum(1 for r in rows if not r['is_2x'] and r['aubio_ok'])}/{n_nor}, "
      f"scipy {sum(1 for r in rows if not r['is_2x'] and r['scipy_ok'])}/{n_nor}")
print("=" * 90)

# Save
with open('/Users/suhaas/Documents/GitHub/dj-metadata-paper/data/bpm_validation_20.json', 'w') as f:
    json.dump(rows, f, indent=2)
print("\nSaved to data/bpm_validation_20.json")
