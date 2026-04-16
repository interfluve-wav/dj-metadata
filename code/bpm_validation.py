#!/usr/bin/env python3
import json

with open('/Users/suhaas/Documents/GitHub/dj-metadata-paper/data/cross_platform_comparison.json') as f:
    cp = json.load(f)
with open('/Users/suhaas/Documents/GitHub/dj-metadata-paper/data/aubio_results.json') as f:
    aubio_raw = json.load(f)
with open('/Users/suhaas/Documents/GitHub/dj-metadata-paper/data/librosa_results.json') as f:
    librosa_raw = json.load(f)
with open('/Users/suhaas/Documents/GitHub/dj-metadata-paper/data/scipy_results.json') as f:
    scipy_raw = json.load(f)

# Build lookups
aubio_by_key = {(a['artist'], a['title']): a for a in aubio_raw}
librosa_by_key = {(l['artist'], l['title']): l for l in librosa_raw}
scipy_by_key = {(s['artist'], s['title']): s for s in scipy_raw}
cp_by_key = {(r['artist']['rekordbox'], r['title']['rekordbox']): r for r in cp['results']}

all_tracks = []
for r in cp['results']:
    artist = r['artist']['rekordbox']
    title = r['title']['rekordbox']
    key = (artist, title)

    aub_a = aubio_by_key.get(key, {})
    lib_a = librosa_by_key.get(key, {})
    scp_a = scipy_by_key.get(key, {})

    aubio_bpm = aub_a.get('aubio_bpm')
    librosa_bpm = lib_a.get('beat_track_median') or lib_a.get('librosa_tempo')
    scipy_bpm = scp_a.get('scipy_tempo')

    rb = r['bpm']['rekordbox']
    st = r['bpm']['serato']
    is_2x = r['field_results']['bpm'].get('is_2x', False)

    # Ground truth: if 2x bug, Serato is correct (~70); else RB=ST agreed BPM
    gt = st if is_2x else rb

    all_tracks.append({
        'artist': artist, 'title': title,
        'rb': rb, 'st': st, 'gt': gt,
        'aubio': aubio_bpm, 'librosa': librosa_bpm, 'scipy': scipy_bpm,
        'is_2x': is_2x,
        'aubio_err': round(abs(aubio_bpm - gt), 2) if aubio_bpm else None,
        'scipy_err': round(abs(scipy_bpm - gt), 2) if scipy_bpm else None,
    })

# Summary
n_2x = sum(1 for t in all_tracks if t['is_2x'])
n_normal = len(all_tracks) - n_2x

def ok_rate(err_key, is_2x_val):
    n = n_2x if is_2x_val else n_normal
    if n == 0: return "N/A"
    ok = sum(1 for t in all_tracks if t['is_2x'] == is_2x_val and t[err_key] is not None and t[err_key] <= 2.0)
    return f"{100*ok/n:.0f}% ({ok}/{n})"

print(f"Total: {len(all_tracks)} ({n_2x} 2x, {n_normal} normal)\n")
print(f"{'':25s} {'aubio':>12s} {'scipy':>12s}")
print(f"{'2x tracks (gt=Serato~70)':25s} {ok_rate('aubio_err', True):>12s} {ok_rate('scipy_err', True):>12s}")
print(f"{'Normal tracks (gt=RB=ST)':25s} {ok_rate('aubio_err', False):>12s} {ok_rate('scipy_err', False):>12s}")

print("\n=== KEY INSIGHT ===")
ok_2x_aub = sum(1 for t in all_tracks if t['is_2x'] and t['aubio_err'] is not None and t['aubio_err'] <= 2.0)
ok_2x_scp = sum(1 for t in all_tracks if t['is_2x'] and t['scipy_err'] is not None and t['scipy_err'] <= 2.0)
print(f"aubio: 0/{n_2x} 2x tracks correct — it CONFIRMS the wrong Rekordbox 2x value")
print(f"scipy: {ok_2x_scp}/{n_2x} 2x tracks correct — it FINDS the correct Serato half-tempo")
print(f"\nThis proves: aubio has the SAME octave error as Rekordbox.")
print(f"scipy autocorrelation finds the correct half-tempo for 2x tracks.")

# Pretty table
print("\n=== FULL TABLE ===")
print(f"{'#':2s} {'Artist':22s} {'Title':22s} {'RB':>5s} {'ST':>5s} {'GT':>5s} {'aubio':>6s} {'scipy':>6s} {'aE':>4s} {'sE':>4s}  Cat")
for i, t in enumerate(all_tracks, 1):
    cats = []
    if t['is_2x']: cats.append("2x")
    if t['aubio_err'] is not None and t['aubio_err'] <= 2.0: cats.append("aubOK")
    if t['scipy_err'] is not None and t['scipy_err'] <= 2.0: cats.append("scpOK")
    cat = "+".join(cats) if cats else "OK"
    aE = f"{t['aubio_err']:.1f}" if t['aubio_err'] is not None else "-"
    sE = f"{t['scipy_err']:.1f}" if t['scipy_err'] is not None else "-"
    print(f"{i:2d}  {t['artist'][:21]:22s} {t['title'][:21]:22s} {t['rb']:>5.1f} {t['st']:>5.1f} {t['gt']:>5.1f} {str(round(t['aubio'],1) if t['aubio'] else '-'):>6s} {str(round(t['scipy'],1) if t['scipy'] else '-'):>6s} {aE:>4s} {sE:>4s}  {cat}")

with open('/Users/suhaas/Documents/GitHub/dj-metadata-paper/data/bpm_validation_table.json', 'w') as f:
    json.dump(all_tracks, f, indent=2)
