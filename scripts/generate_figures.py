#!/usr/bin/env python3
"""
Generate all 5 figures for the DJ Metadata Paper.
Uses placeholder data — replace with actual experimental results.

Usage:
    python generate_figures.py
    # Outputs PDFs to figures/ directory
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path

# ISMIR-style settings
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
})

OUT = Path("figures")
OUT.mkdir(exist_ok=True)

# =========================================================================
# Placeholder data (replace with actual results)
# =========================================================================

PLATFORMS = ['Rekordbox', 'Serato', 'Traktor']
PATHS = ['R→S', 'R→T', 'S→R', 'S→T', 'T→R', 'T→S']

# AQS per path (placeholder)
AQS = np.array([
    [1.00, 0.87, 0.82, 0.78, 0.86, 0.80],  # R→S, R→T, S→R, S→T, T→R, T→S
    [0.87, 1.00, 0.85, 0.84, 0.79, 0.83],
    [0.82, 0.85, 1.00, 0.83, 0.80, 0.81],
    [0.78, 0.84, 0.83, 1.00, 0.76, 0.82],
    [0.86, 0.79, 0.80, 0.76, 1.00, 0.84],
    [0.80, 0.83, 0.81, 0.82, 0.84, 1.00],
])
# Diagonal should be 1.0
np.fill_diagonal(AQS, 1.0)

# Per-field PR by tier (placeholder)
FIELDS_TIER1 = ['BPM', 'Bitrate', 'Sample Rate', 'Duration']
FIELDS_TIER2 = ['Genre', 'Label', 'Key']
FIELDS_TIER3 = ['Energy', 'Mood', 'Rating', 'Playlist']

PR_TIER1 = np.array([
    [0.998, 0.995, 0.999, 0.997, 0.994, 0.998],  # BPM
    [0.999, 0.999, 0.998, 0.999, 0.997, 0.999],  # Bitrate
    [0.999, 0.999, 0.999, 0.999, 0.998, 0.999],  # Sample Rate
    [0.997, 0.996, 0.998, 0.997, 0.995, 0.997],  # Duration
])

PR_TIER2 = np.array([
    [0.84, 0.72, 0.79, 0.66, 0.74, 0.70],  # Genre
    [0.81, 0.75, 0.78, 0.71, 0.73, 0.72],  # Label
    [0.78, 0.71, 0.76, 0.73, 0.71, 0.74],  # Key
])

PR_TIER3 = np.array([
    [0.00, 0.00, 0.88, 0.00, 0.86, 0.00],  # Energy
    [0.00, 0.00, 0.82, 0.00, 0.80, 0.00],  # Mood
    [0.72, 0.68, 0.75, 0.65, 0.70, 0.67],  # Rating
    [0.52, 0.41, 0.48, 0.38, 0.45, 0.40],  # Playlist
])

# Round-trip data
SINGLE_PR = np.array([0.998, 0.84, 0.78, 0.00, 0.72, 0.52])
ROUNDTRIP_PR = np.array([0.996, 0.69, 0.61, 0.00, 0.58, 0.35])
RT_FIELDS = ['BPM', 'Genre', 'Key', 'Energy', 'Rating', 'Playlist']

# UDMS validation data
ALL_FIELDS = ['BPM', 'Key', 'Genre', 'Label', 'Energy', 'Mood',
              'Rating', 'Playlist', 'Title', 'Artist', 'Album',
              'Bitrate', 'Sample Rate', 'Duration', 'Catalog No',
              'File Path', 'Key Numeric', 'Mood Numeric']
PR_WITHOUT_UDMS = [0.998, 0.71, 0.78, 0.75, 0.00, 0.00,
                   0.72, 0.42, 0.95, 0.94, 0.93,
                   0.999, 0.999, 0.997, 0.65,
                   0.92, 0.71, 0.00]
PR_WITH_UDMS = [0.998, 1.00, 0.99, 0.99, 1.00, 1.00,
                0.99, 0.99, 0.99, 0.99, 0.99,
                0.999, 0.999, 0.997, 0.99,
                0.99, 1.00, 1.00]

# =========================================================================
# Figure 1: Transfer Matrix Heatmap
# =========================================================================

def fig_transfer_matrix():
    fig, ax = plt.subplots(figsize=(4, 3.5))

    # Build 3x3 matrix from the 6 paths
    matrix = np.array([
        [1.00, 0.87, 0.82],  # R→R, R→S, R→T
        [0.86, 1.00, 0.83],  # S→R, S→S, S→T
        [0.78, 0.80, 1.00],  # T→R, T→S, T→T
    ])

    cmap = mcolors.LinearSegmentedColormap.from_list(
        'aqs', ['#d73027', '#fee08b', '#1a9850'], N=256
    )

    im = ax.imshow(matrix, cmap=cmap, vmin=0.70, vmax=1.00, aspect='equal')

    # Annotate cells
    for i in range(3):
        for j in range(3):
            val = matrix[i, j]
            color = 'white' if val < 0.82 else 'black'
            weight = 'bold' if i == j else 'normal'
            ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                    fontsize=12, color=color, fontweight=weight)

    ax.set_xticks(range(3))
    ax.set_yticks(range(3))
    ax.set_xticklabels(PLATFORMS, fontsize=10)
    ax.set_yticklabels(PLATFORMS, fontsize=10)
    ax.set_xlabel('Destination Platform', fontsize=10)
    ax.set_ylabel('Source Platform', fontsize=10)
    ax.set_title('Aggregate Quality Score by Transfer Path', fontsize=11)

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('AQS', fontsize=10)

    fig.tight_layout()
    fig.savefig(OUT / 'fig_transfer_matrix.pdf')
    fig.savefig(OUT / 'fig_transfer_matrix.png')
    plt.close(fig)
    print(f"  Saved fig_transfer_matrix.pdf")


# =========================================================================
# Figure 2: Field Taxonomy Bar Chart
# =========================================================================

def fig_field_taxonomy():
    fig, axes = plt.subplots(1, 3, figsize=(7, 3), sharey=True)

    tiers = [
        ('Tier 1: Numeric', FIELDS_TIER1, PR_TIER1, '#2166ac'),
        ('Tier 2: Categorical', FIELDS_TIER2, PR_TIER2, '#f4a582'),
        ('Tier 3: Custom', FIELDS_TIER3, PR_TIER3, '#b2182b'),
    ]

    for ax, (title, fields, pr_data, color) in zip(axes, tiers):
        # Mean PR across all paths
        means = pr_data.mean(axis=1)
        bars = ax.barh(range(len(fields)), means, color=color, alpha=0.85, height=0.6)
        ax.set_yticks(range(len(fields)))
        ax.set_yticklabels(fields, fontsize=8)
        ax.set_xlim(0, 1.05)
        ax.set_xlabel('Preservation Rate')
        ax.set_title(title, fontsize=9, fontweight='bold')
        ax.axvline(x=1.0, color='gray', linestyle='--', alpha=0.3)

        # Add value labels
        for bar, val in zip(bars, means):
            ax.text(val + 0.02, bar.get_y() + bar.get_height()/2,
                    f'{val:.0%}', va='center', fontsize=7)

    fig.suptitle('Preservation Rates by Field Tier (Mean Across All Paths)',
                 fontsize=10, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / 'fig_field_taxonomy.pdf')
    fig.savefig(OUT / 'fig_field_taxonomy.png')
    plt.close(fig)
    print(f"  Saved fig_field_taxonomy.pdf")


# =========================================================================
# Figure 3: Round-Trip Degradation
# =========================================================================

def fig_roundtrip():
    fig, ax = plt.subplots(figsize=(5, 3))

    x = np.arange(len(RT_FIELDS))
    width = 0.35

    bars1 = ax.bar(x - width/2, SINGLE_PR, width, label='Single Transfer',
                   color='#2166ac', alpha=0.85)
    bars2 = ax.bar(x + width/2, ROUNDTRIP_PR, width, label='Round-Trip (p→q→p)',
                   color='#d6604d', alpha=0.85)

    ax.set_ylabel('Preservation Rate')
    ax.set_title('Single Transfer vs. Round-Trip Preservation', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(RT_FIELDS, rotation=30, ha='right', fontsize=8)
    ax.set_ylim(0, 1.1)
    ax.legend(loc='upper right', fontsize=8)
    ax.axhline(y=0.90, color='gray', linestyle='--', alpha=0.4, label='90% threshold')

    # Annotate degradation
    for i, (s, r) in enumerate(zip(SINGLE_PR, ROUNDTRIP_PR)):
        if s > 0 and r > 0:
            delta = s - r
            ax.annotate(f'-{delta:.0%}', xy=(i + width/2, r),
                       xytext=(0, -12), textcoords='offset points',
                       ha='center', fontsize=7, color='#b2182b')

    fig.tight_layout()
    fig.savefig(OUT / 'fig_roundtrip_degradation.pdf')
    fig.savefig(OUT / 'fig_roundtrip_degradation.png')
    plt.close(fig)
    print(f"  Saved fig_roundtrip_degradation.pdf")


# =========================================================================
# Figure 4: UDMS Validation Comparison
# =========================================================================

def fig_udms_validation():
    fig, ax = plt.subplots(figsize=(6, 3.5))

    # Sort by difference
    diffs = [abs(w - u) for w, u in zip(PR_WITHOUT_UDMS, PR_WITH_UDMS)]
    order = np.argsort(diffs)[::-1]

    fields_sorted = [ALL_FIELDS[i] for i in order]
    without_sorted = [PR_WITHOUT_UDMS[i] for i in order]
    with_sorted = [PR_WITH_UDMS[i] for i in order]

    y = np.arange(len(fields_sorted))
    height = 0.35

    ax.barh(y - height/2, without_sorted, height, label='Without UDMS',
            color='#d6604d', alpha=0.85)
    ax.barh(y + height/2, with_sorted, height, label='With UDMS',
            color='#1a9850', alpha=0.85)

    ax.set_yticks(y)
    ax.set_yticklabels(fields_sorted, fontsize=7)
    ax.set_xlabel('Preservation Rate')
    ax.set_title('UDMS Normalization Impact by Field', fontweight='bold')
    ax.set_xlim(0, 1.08)
    ax.legend(loc='lower right', fontsize=8)
    ax.axvline(x=1.0, color='gray', linestyle='--', alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUT / 'fig_udms_validation.pdf')
    fig.savefig(OUT / 'fig_udms_validation.png')
    plt.close(fig)
    print(f"  Saved fig_udms_validation.pdf")


# =========================================================================
# Figure 5: Degradation Examples
# =========================================================================

def fig_degradation_examples():
    fig, axes = plt.subplots(1, 3, figsize=(7, 3))

    # Example 1: Genre enum mismatch
    ax = axes[0]
    genres_rekordbox = ['Electronic', 'Hip-Hop', 'Rock', 'Jazz', 'Latin', 'Classical']
    genres_serato = ['Dance', 'Hip-Hop', 'Rock', 'Jazz', 'Latin', 'Classical']
    preserved = [0, 1, 1, 1, 1, 1]  # "Electronic" → "Dance" = lost
    colors = ['#1a9850' if p else '#d6604d' for p in preserved]
    ax.barh(range(len(genres_rekordbox)), [1]*6, color=colors, alpha=0.7, height=0.6)
    for i, (rb, st) in enumerate(zip(genres_rekordbox, genres_serato)):
        label = f'{rb} → {st}' if rb != st else rb
        ax.text(0.5, i, label, ha='center', va='center', fontsize=7,
                fontweight='bold' if rb != st else 'normal')
    ax.set_xlim(0, 1)
    ax.set_yticks([])
    ax.set_title('Genre Enum Mismatch\n(R → S)', fontsize=9, fontweight='bold')
    ax.set_xticks([])

    # Example 2: Key notation conversion
    ax = axes[1]
    keys_rb = ['Am', 'Cm', 'Em', 'Gm', 'Bm', 'Dm']
    keys_camelot = ['8A', '5A', '9A', '6A', '10A', '7A']
    preserved_k = [1, 1, 1, 1, 0, 1]  # Bm → 10A is ambiguous
    colors_k = ['#1a9850' if p else '#d6604d' for p in preserved_k]
    ax.barh(range(len(keys_rb)), [1]*6, color=colors_k, alpha=0.7, height=0.6)
    for i, (rb, cm) in enumerate(zip(keys_rb, keys_camelot)):
        ax.text(0.5, i, f'{rb} → {cm}', ha='center', va='center', fontsize=7,
                fontweight='bold' if not preserved_k[i] else 'normal')
    ax.set_xlim(0, 1)
    ax.set_yticks([])
    ax.set_title('Key Notation Conversion\n(R → S)', fontsize=9, fontweight='bold')
    ax.set_xticks([])

    # Example 3: Energy rating loss
    ax = axes[2]
    fields = ['Energy', 'Mood', 'Rating', 'Playlist']
    pres_rb_to_t = [0.00, 0.00, 0.68, 0.41]
    colors_e = ['#d6604d' if v < 0.5 else '#fee08b' if v < 0.8 else '#1a9850'
                for v in pres_rb_to_t]
    ax.barh(range(len(fields)), pres_rb_to_t, color=colors_e, alpha=0.8, height=0.6)
    for i, v in enumerate(pres_rb_to_t):
        ax.text(v + 0.03, i, f'{v:.0%}', va='center', fontsize=8)
    ax.set_yticks(range(len(fields)))
    ax.set_yticklabels(fields, fontsize=8)
    ax.set_xlim(0, 1.1)
    ax.set_title('Custom Field Loss\n(R → T)', fontsize=9, fontweight='bold')
    ax.set_xlabel('Preservation Rate', fontsize=8)

    fig.suptitle('Metadata Degradation Examples', fontsize=10, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / 'fig_degradation_examples.pdf')
    fig.savefig(OUT / 'fig_degradation_examples.png')
    plt.close(fig)
    print(f"  Saved fig_degradation_examples.pdf")


# =========================================================================
# Main
# =========================================================================

if __name__ == '__main__':
    print("Generating figures for DJ Metadata Paper...")
    fig_transfer_matrix()
    fig_field_taxonomy()
    fig_roundtrip()
    fig_udms_validation()
    fig_degradation_examples()
    print(f"\nAll figures saved to {OUT}/")
    print("NOTE: These use placeholder data. Replace with actual experimental results.")
