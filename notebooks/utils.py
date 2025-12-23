import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns


import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Human-readable number formatting (K/M/B)
def human_int(n):
    n = float(n)
    if n >= 1_000_000_000: return f"{n/1_000_000_000:.1f}B"
    if n >= 1_000_000:     return f"{n/1_000_000:.1f}M"
    if n >= 1_000:         return f"{n/1_000:.1f}K"
    return f"{n:.0f}"

def plot_hist_log_highlight_median(
    ax,
    s_raw,
    title,
    xlabel,
    ticks_raw,
    prefix="",
    suffix="",
    clip_q=0.99,
    bins_n=40,
    text_offset_factor=1.0,
    color="#1f77b4"
):
    # Convert to numeric and filter positives
    s = pd.to_numeric(s_raw, errors="coerce").dropna()
    s = s[s > 0]

    # Handle empty data
    if len(s) == 0:
        ax.set_title(title, fontweight="bold")
        ax.text(0.5, 0.5, "No positive data", ha="center", va="center", transform=ax.transAxes)
        return

    # Clip extreme values if enabled
    if clip_q is not None:
        s = s.clip(upper=s.quantile(clip_q))

    # Build log-spaced bins
    lo, hi = float(s.min()), float(s.max())
    bins = np.logspace(np.log10(lo), np.log10(hi), bins_n)

    # Draw histogram bars only
    counts, edges, patches = ax.hist(
        s,
        bins=bins,
        alpha=0.85,
        color=color,
        edgecolor='white',
        linewidth=0.5
    )

    # Set log x-axis
    ax.set_xscale("log")

    # Compute median and locate its bin
    med = float(np.median(s))
    idx = np.searchsorted(edges, med, side="right") - 1
    idx = int(np.clip(idx, 0, len(patches) - 1))

    # Highlight the median bin
    patches[idx].set_facecolor("#d62728")
    patches[idx].set_alpha(1.0)
    patches[idx].set_edgecolor("black")

    # Place median label above the bar
    bar_height = counts[idx]
    bar_center = np.sqrt(edges[idx] * edges[idx + 1])
    text_x_pos = bar_center * text_offset_factor

    ax.text(
        text_x_pos,
        bar_height,
        f"{prefix}{human_int(med)}{suffix}",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold",
        color="#d62728"
    )

    # Set titles and axis formatting
    ax.set_title(title, fontweight="bold")
    if ticks_raw:
        ticks_use = [t for t in ticks_raw if lo <= t <= hi]
        if not ticks_use:
            ticks_use = [lo, hi]
        ax.set_xticks(ticks_use)

    # Remove minor ticks
    ax.xaxis.set_minor_locator(mticker.NullLocator())
    # Set labels and grid
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Number of events")
    ax.grid(True, alpha=0.25)

# Compact currency formatting
def currency_format(x, pos):
    if x >= 1e9: return f'${x*1e-9:.0f}B'
    if x >= 1e6: return f'${x*1e-6:.0f}M'
    if x >= 1e3: return f'${x*1e-3:.0f}K'
    return f'${x:.0f}'

formatter = ticker.FuncFormatter(currency_format)

# Compact number formatting
def human_format(x, pos):
    if x >= 1e9: return f'{x*1e-9:.0f}B'
    if x >= 1e6: return f'{x*1e-6:.0f}M'
    if x >= 1e3: return f'{x*1e-3:.0f}K'
    return f'{x:.0f}'

# Currency formatting using human_format
def currency_format(x, pos):
    return f"${human_format(x, pos)}"

# Currency formatting with optional decimals
def currency_format2(x, pos):
    if x >= 1e9: return f'${x*1e-9:.1f}B'
    if x >= 1e6: return f'${x*1e-6:.1f}M'
    if x >= 1e3: return f'${x*1e-3:.0f}K'
    return f'${x:.0f}'
