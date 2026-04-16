#!/usr/bin/env python3
"""
Generate cross-platform analysis figures from real matched track data.
Uses data/cross_platform_comparison.json and data/fig_cross_platform_data.json.
"""

import json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

repo = Path(__file__).parent.parent
OUT = repo / 'paper'
OUT.mkdir(exist_ok=True)

# Load data
with open(repo / 'data/cross_platform_comparison.json') as f:
    data = json.load(f)
results = data['results']

# ============================================================
# Figure: Cross-Platform BPM Distribution
# ============================================================
def fig_cross_platform_bpm():
    """BPM distribution across 143 matched tracks, color-coded by 2x bug."""
    bpm_vals = []
    bpm_2x = []
    bpm_raw = []
    for r in results:
        b = r['bpm']['rekordbox']
        if b and b > 0:
            bpm_vals.append(b)
            if r['field_results']['bpm'].get('is_2x'):
                bpm_2x.append(b)
            else:
                bpm_raw.append(b)

    # Build histogram buckets
    buckets = ['70-79', '80-89', '90-99', '100-109', '110-119',
               '120-129', '130-139', '140-149', '150-159', '160-169', '170-179']
    bin_edges = [70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180]

    raw_counts = []
    bug_counts = []
    for i in range(len(buckets)):
        lo, hi = bin_edges[i], bin_edges[i+1]
        raw_counts.append(sum(1 for v in bpm_raw if lo <= v < hi))
        bug_counts.append(sum(1 for v in bpm_2x if lo <= v < hi))

    fig, ax = plt.subplots(figsize=(5, 3))

    x = range(len(buckets))
    bar_width = 0.6
    bars_raw = ax.bar(x, raw_counts, bar_width, color='#2166ac', alpha=0.85, label='Normal BPM')
    bars_bug = ax.bar(x, bug_counts, bar_width, color='#d6604d', alpha=0.85, label='Rekordbox 2× bug')

    ax.set_xticks(list(x))
    ax.set_xticklabels(buckets, fontsize=7.5, rotation=45)
    ax.set_xlabel('BPM (Rekordbox)', fontsize=9)
    ax.set_ylabel('Track Count', fontsize=9)
    ax.set_title('BPM Distribution — 143 Matched Tracks (Rekordbox)', fontsize=10)

    # Annotate 2x bug buckets
    for i, (raw, bug) in enumerate(zip(raw_counts, bug_counts)):
        if bug > 0:
            ax.text(i, bug + 0.5, f'+{bug}', ha='center', fontsize=7, color='#b2182b', fontweight='bold')

    ax.legend(fontsize=8, loc='upper left')
    ax.set_ylim(0, max(max(raw_counts), max(bug_counts)) + 5)
    ax.yaxis.grid(True, alpha=0.3)
    ax.set_axisbelow(True)

    mean_raw = sum(bpm_raw)/len(bpm_raw) if bpm_raw else 0
    ax.axvline(x=list(x)[6], color='gray', linestyle='--', alpha=0.4)  # ~130 BPM
    ax.text(6.1, max(raw_counts)*0.9, f'μ={mean_raw:.0f}', fontsize=7.5, color='gray')

    fig.tight_layout()
    fig.savefig(OUT / 'fig_cross_platform_bpm.pdf', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved fig_cross_platform_bpm.pdf")


# ============================================================
# Figure: Genre Entropy & Fragmentation
# ============================================================
def fig_genre_entropy():
    """Show genre fragmentation: Shannon entropy vs effective number of genres."""
    from collections import Counter

    genre_rb = Counter(r['genre']['rekordbox'] for r in results if r['genre'].get('rekordbox'))
    total_rb = sum(genre_rb.values())

    # Shannon entropy
    H_rb = -sum((c/total_rb) * math.log2(c/total_rb) for c in genre_rb.values())
    max_H_rb = math.log2(len(genre_rb))
    eff_rb = 1 / sum((c/total_rb)**2 for c in genre_rb.values())

    genres_sorted = sorted(genre_rb.items(), key=lambda x: -x[1])[:15]
    counts = [c for g, c in genres_sorted]
    labels = [g for g, c in genres_sorted]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 3))

    # Left: bar chart of top genres
    colors = ['#2166ac'] * len(labels)
    ax1.barh(range(len(labels)), counts, color='#2166ac', alpha=0.85, height=0.6)
    ax1.set_yticks(range(len(labels)))
    ax1.set_yticklabels(labels, fontsize=7.5)
    ax1.set_xlabel('Track Count', fontsize=9)
    ax1.set_title('Top Genres (Rekordbox)', fontsize=10)
    ax1.invert_yaxis()
    for i, c in enumerate(counts):
        ax1.text(c + 0.2, i, str(c), va='center', fontsize=7.5)

    # Right: entropy metrics
    ax2.axis('off')
    metrics = [
        ('Unique genres', len(genre_rb)),
        ('Tagged tracks', total_rb),
        ('Shannon entropy', f'{H_rb:.2f} bits'),
        ('Max entropy', f'{max_H_rb:.2f} bits'),
        ('Normalized', f'{100*H_rb/max_H_rb:.1f}%'),
        ('Effective # genres', f'{eff_rb:.1f}'),
    ]
    y_positions = [0.85 - i*0.12 for i in range(len(metrics))]
    for i, (label, value) in enumerate(metrics):
        ax2.text(0.05, y_positions[i], f'{label}:', fontsize=10, fontweight='bold')
        ax2.text(0.55, y_positions[i], str(value), fontsize=10)

    ax2.set_title('Genre Diversity Metrics', fontsize=10)

    fig.tight_layout()
    fig.savefig(OUT / 'fig_genre_entropy.pdf', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved fig_genre_entropy.pdf")


# ============================================================
# Figure: Key Distribution (Matched Tracks)
# ============================================================
def fig_key_distribution():
    """Camelot key distribution for 143 matched tracks."""
    from collections import Counter
    key_rb = Counter(r['key']['rekordbox'] for r in results
                    if r['key'].get('rekordbox') and r['key']['rekordbox'] != 'Unknown')
    total = sum(key_rb.values())

    minor_keys = {k: v for k, v in key_rb.items() if k.endswith('A')}
    major_keys = {k: v for k, v in key_rb.items() if k.endswith('B')}

    fig, ax = plt.subplots(figsize=(5, 3))

    keys_sorted = sorted(key_rb.items(), key=lambda x: int(x[0][:-1]))
    labels = [k for k, v in keys_sorted]
    counts = [v for k, v in keys_sorted]
    colors = ['#d6604d' if k.endswith('A') else '#2166ac' for k in labels]

    x = range(len(labels))
    bars = ax.bar(x, counts, color=colors, alpha=0.85, width=0.6)

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_xlabel('Camelot Key', fontsize=9)
    ax.set_ylabel('Track Count', fontsize=9)
    ax.set_title(f'Camelot Key Distribution — {total} Keyed Tracks', fontsize=10)

    minor_patch = mpatches.Patch(color='#d6604d', alpha=0.85, label=f'Minor (A): {sum(minor_keys.values())} ({100*sum(minor_keys.values())/total:.1f}%)')
    major_patch = mpatches.Patch(color='#2166ac', alpha=0.85, label=f'Major (B): {sum(major_keys.values())} ({100*sum(major_keys.values())/total:.1f}%)')
    ax.legend(handles=[minor_patch, major_patch], fontsize=8)

    ax.yaxis.grid(True, alpha=0.3)
    ax.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig(OUT / 'fig_cross_platform_key.pdf', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved fig_cross_platform_key.pdf")


if __name__ == '__main__':
    print("Generating cross-platform figures...")
    fig_cross_platform_bpm()
    fig_genre_entropy()
    fig_key_distribution()
    print("\nDone.")
