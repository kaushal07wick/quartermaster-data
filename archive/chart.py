import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

# --- Config ---
INPUT_FILE = "cumulative_volume_chart.csv"
PALETTE = {
    "CEX": "#1155cc",  # Darker blue
    "DEX": "#ff7f0e",  # Orange
}

def human_format(num):
    for unit in ['', 'K', 'M', 'B', 'T']:
        if abs(num) < 1000:
            return f"${num:,.0f}{unit}"
        num /= 1000
    return f"${num:.1f}Q"

# --- Load and prepare data ---
df = pd.read_csv(INPUT_FILE, parse_dates=["Date"])
df = df.sort_values("Date")

# Select 4 spaced ticks
all_dates = df["Date"].drop_duplicates().sort_values()
step = len(all_dates) // 3
tick_dates = [all_dates.iloc[i] for i in [0, step, step * 2, -1]]
tick_labels = [d.strftime("%b %Y") for d in tick_dates]

# --- Plot ---
sns.set_style("white")
fig, ax = plt.subplots(figsize=(16, 8))

# Area for CEX
ax.fill_between(df["Date"], df["CEX"], color=PALETTE["CEX"], alpha=0.35, label="CEX")

# Bar for DEX
ax.bar(df["Date"], df["DEX"], width=2.0, color=PALETTE["DEX"], alpha=0.9, label="DEX")

# Y-axis formatting
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: human_format(x)))
ax.set_ylim(bottom=0)
ax.set_xlim(df["Date"].min(), df["Date"].max())

# X-axis formatting
ax.set_xticks(tick_dates)
ax.set_xticklabels(tick_labels)
ax.set_xlabel("Date", fontsize=12)
ax.set_ylabel("Volume (USD)", fontsize=12)

# Remove grid
sns.despine()

# Add titles
plt.suptitle("Historical (1y) Comparison: Top 10 CEXs vs Top 10 DEXs", fontsize=18, y=1.03)
plt.title("This data is based on the top 10 DEXs and CEXs in terms of volume. The comparison combines spot and perpetuals volumes.",
          fontsize=12, style='italic', y=1.01)

# Legend
ax.legend(title="Exchange Type")

# Tight margins
plt.margins(x=0.005, y=0.05)
plt.tight_layout()

# Save and show
plt.savefig("volume_comparison_final.png", dpi=300, bbox_inches="tight")
#plt.show()
