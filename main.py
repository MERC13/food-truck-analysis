"""
BobaLab Case Study — Analysis Script
=====================================
Reads input CSV files from data/ and writes figures to results/.
Prints all results to stdout.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from project_paths import data_file, ensure_results_dir


plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update(
    {
        "figure.dpi": 120,
        "savefig.dpi": 220,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 9,
        "font.size": 10,
    }
)

REC_COLORS = {1: "#2F6DAE", 2: "#4E9E6A", 3: "#D98E3A"}
SOCIAL_COLORS = {"agree": "#586B7D", "against": "#B24C4C"}
CI_COLOR = "#2C3E50"
RESULTS_DIR = ensure_results_dir()
ROUND_PATH = data_file("foodtruck_clean_rounds.csv")
SUMMARY_PATH = data_file("foodtruck_participant_summary.csv")
ATTEMPTS_PATH = data_file("foodtruck_clean_attempts.csv")
HEATMAP_PATH = RESULTS_DIR / "day_hour_choice_probability_heatmaps.png"
RECOMMENDATION_CI_PATH = RESULTS_DIR / "days_3_5_recommendation_ci.png"
SOCIAL_CI_PATH = RESULTS_DIR / "days_6_8_social_recommendation_ci.png"
MICROCLUSTER_CI_PATH = RESULTS_DIR / "microcluster_profiles_3_ci.png"


def mean_bootstrap_ci(values, n_boot=2000, alpha=0.05, seed=42):
    arr = pd.Series(values).dropna().to_numpy(dtype=float)
    n = len(arr)
    if n == 0:
        return np.nan, np.nan, np.nan, 0
    mean = float(np.mean(arr))
    if n == 1:
        return mean, mean, mean, 1

    rng = np.random.default_rng(seed)
    samples = rng.choice(arr, size=(n_boot, n), replace=True)
    stats = np.mean(samples, axis=1)
    lower, upper = np.percentile(stats, [100 * (alpha / 2), 100 * (1 - alpha / 2)])
    return mean, float(lower), float(upper), n


def wilson_ci(successes, n, alpha=0.05):
    if n == 0:
        return np.nan, np.nan, np.nan
    z = 1.959963984540054
    p = successes / n
    denom = 1 + (z**2 / n)
    center = (p + (z**2 / (2 * n))) / denom
    margin = (z * np.sqrt((p * (1 - p) / n) + (z**2 / (4 * n**2)))) / denom
    return float(p), float(max(0.0, center - margin)), float(min(1.0, center + margin))


def summarize_binary(df, group_cols, value_col):
    rows = []
    grouped = df.groupby(group_cols, dropna=False)
    for keys, sub in grouped:
        values = sub[value_col].dropna().astype(float)
        n = int(len(values))
        successes = int(np.round(values.sum())) if n else 0
        rate, lower, upper = wilson_ci(successes, n)
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = {col: key for col, key in zip(group_cols, keys)}
        row.update({"mean": rate, "ci_low": lower, "ci_high": upper, "n": n})
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_numeric(df, group_cols, value_col):
    rows = []
    grouped = df.groupby(group_cols, dropna=False)
    for keys, sub in grouped:
        mean, lower, upper, n = mean_bootstrap_ci(sub[value_col])
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = {col: key for col, key in zip(group_cols, keys)}
        row.update({"mean": mean, "ci_low": lower, "ci_high": upper, "n": n})
        rows.append(row)
    return pd.DataFrame(rows)


def quantile_buckets(series, n_bins=5):
    series = pd.Series(series)
    valid = series.dropna()
    if valid.empty:
        empty = pd.Series([np.nan] * len(series), index=series.index)
        return empty, []

    unique = valid.nunique()
    if unique < 2:
        label = f"{valid.iloc[0]:.2f}"
        filled = pd.Series([label] * len(series), index=series.index)
        return filled, [label]

    bins = pd.qcut(series, q=min(n_bins, unique), duplicates="drop")
    return bins.astype(str), [str(cat) for cat in bins.cat.categories]


def style_axis(ax):
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)


def build_legend_handles(labels, palette):
    return [Patch(facecolor=palette[label], edgecolor="white", label=str(label)) for label in labels]


def plot_grouped_bars(
    ax,
    df,
    x_col,
    order,
    y_col="mean",
    ci_low_col="ci_low",
    ci_high_col="ci_high",
    hue_col=None,
    hue_order=None,
    palette=None,
    ylabel=None,
    xlabel=None,
    title=None,
    width=0.22,
    legend_title=None,
    bar_colors=None,
    show_legend=True,
):
    style_axis(ax)
    x_positions = np.arange(len(order))

    if hue_col is None:
        subset = df.set_index(x_col).reindex(order)
        if bar_colors is None:
            bar_colors = [CI_COLOR] * len(order)
        ax.errorbar(
            x_positions,
            subset[y_col].to_numpy(dtype=float),
            yerr=[
                subset[y_col].to_numpy(dtype=float) - subset[ci_low_col].to_numpy(dtype=float),
                subset[ci_high_col].to_numpy(dtype=float) - subset[y_col].to_numpy(dtype=float),
            ],
            fmt="o-",
            color=CI_COLOR,
            lw=2,
            capsize=4,
            markersize=5,
        )
        ax.collections[-1].set_visible(False)
        ax.lines[-1].set_visible(False)
        ax.bar(
            x_positions,
            subset[y_col].to_numpy(dtype=float),
            width=0.55,
            color=bar_colors,
            alpha=0.9,
            edgecolor="white",
            linewidth=0.8,
        )
        ax.errorbar(
            x_positions,
            subset[y_col].to_numpy(dtype=float),
            yerr=[
                subset[y_col].to_numpy(dtype=float) - subset[ci_low_col].to_numpy(dtype=float),
                subset[ci_high_col].to_numpy(dtype=float) - subset[y_col].to_numpy(dtype=float),
            ],
            fmt="none",
            ecolor=CI_COLOR,
            elinewidth=1.2,
            capsize=4,
        )
    else:
        if hue_order is None:
            hue_order = list(df[hue_col].dropna().unique())
        if palette is None:
            palette = {hue: CI_COLOR for hue in hue_order}
        offsets = np.linspace(-width * (len(hue_order) - 1) / 2, width * (len(hue_order) - 1) / 2, len(hue_order))

        for offset, hue in zip(offsets, hue_order):
            subset = df[df[hue_col] == hue].set_index(x_col).reindex(order)
            values = subset[y_col].to_numpy(dtype=float)
            lower = subset[ci_low_col].to_numpy(dtype=float)
            upper = subset[ci_high_col].to_numpy(dtype=float)
            xpos = x_positions + offset
            ax.bar(
                xpos,
                values,
                width=width,
                color=palette.get(hue, CI_COLOR),
                alpha=0.88,
                label=str(hue),
                edgecolor="white",
                linewidth=0.8,
            )
            ax.errorbar(
                xpos,
                values,
                yerr=[values - lower, upper - values],
                fmt="none",
                ecolor=CI_COLOR,
                elinewidth=1.2,
                capsize=3,
            )

    ax.set_xticks(x_positions)
    ax.set_xticklabels(order)
    if ylabel:
        ax.set_ylabel(ylabel)
    if xlabel:
        ax.set_xlabel(xlabel)
    if title:
        ax.set_title(title)
    if hue_col is not None and show_legend:
        ax.legend(title=legend_title, frameon=False, ncols=min(len(hue_order), 3))


def add_figure_legend(fig, labels, palette, title, ncol, anchor_y=-0.02):
    fig.legend(
        handles=build_legend_handles(labels, palette),
        loc="lower center",
        bbox_to_anchor=(0.5, anchor_y),
        ncol=ncol,
        frameon=False,
        title=title,
    )


def build_day_value_cache(real_df):
    cache = {}
    for day, day_df in real_df.groupby("day"):
        day_data = day_df.sort_values("hour").drop_duplicates(subset=["hour"])
        customers = np.zeros((NUM_PARKS, NUM_HOURS))
        trucks = np.zeros((NUM_PARKS, NUM_HOURS))
        for _, row in day_data.iterrows():
            h = int(row["hour"]) - 1
            customers[0, h] = row["park1_people"]
            customers[1, h] = row["park2_people"]
            customers[2, h] = row["park3_people"]
            trucks[0, h] = row["park1_trucks"]
            trucks[1, h] = row["park2_trucks"]
            trucks[2, h] = row["park3_trucks"]

        reward = np.divide(customers, trucks, out=np.zeros_like(customers, dtype=float), where=trucks > 0)
        q_values = np.zeros((NUM_PARKS, NUM_HOURS))
        value_fn = np.zeros(NUM_HOURS + 1)
        for hour_idx in range(NUM_HOURS - 1, -1, -1):
            for park_idx in range(NUM_PARKS):
                q_values[park_idx, hour_idx] = reward[park_idx, hour_idx] + value_fn[hour_idx + 1]
            value_fn[hour_idx] = np.max(q_values[:, hour_idx])

        cache[int(day)] = {"Q": q_values, "V": value_fn}

    return cache


def row_shortfall(row, cache):
    day = int(row["day"])
    hour_idx = int(row["hour"]) - 1
    chosen = int(row["chosen_park_idx"])
    day_cache = cache[day]
    return float(day_cache["V"][hour_idx] - day_cache["Q"][chosen, hour_idx])


def save_figure(fig, filename):
    filename.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(filename, dpi=220, bbox_inches="tight")
    plt.close(fig)

# ── Load data ──────────────────────────────────────────────────────────
rounds = pd.read_csv(ROUND_PATH)
summary = pd.read_csv(SUMMARY_PATH)

real = rounds[rounds["is_real_participant"] == True].copy()
NUM_PARKS = 3
NUM_HOURS = 5
TOTAL_TRUCKS = 20

# Map advice_freq codes to labels
FREQ_LABELS = {1: "10%", 2: "50%", 3: "90%"}
real["freq_label"] = real["advice_freq_assigned"].map(FREQ_LABELS)


# ======================================================================
# 1) OPTIMAL Q-VALUES AND POLICY
# ======================================================================
print("=" * 70)
print("1) OPTIMAL Q-VALUES AND POLICY PER DAY")
print("=" * 70)

days = sorted(real["day"].unique())

for day in days:
    day_data = real[(real["day"] == day)].drop_duplicates(subset=["hour"])

    # Extract realized customers and trucks per park per hour
    customers = np.zeros((NUM_PARKS, NUM_HOURS))
    trucks = np.zeros((NUM_PARKS, NUM_HOURS))
    for _, row in day_data.iterrows():
        h = int(row["hour"]) - 1
        customers[0][h] = row["park1_people"]
        customers[1][h] = row["park2_people"]
        customers[2][h] = row["park3_people"]
        trucks[0][h] = row["park1_trucks"]
        trucks[1][h] = row["park2_trucks"]
        trucks[2][h] = row["park3_trucks"]

    # Immediate reward: customers / trucks
    reward = np.zeros((NUM_PARKS, NUM_HOURS))
    for p in range(NUM_PARKS):
        for h in range(NUM_HOURS):
            reward[p][h] = customers[p][h] / trucks[p][h] if trucks[p][h] > 0 else 0

    # Backward induction
    Q = np.zeros((NUM_PARKS, NUM_HOURS))
    V = np.zeros(NUM_HOURS + 1)
    for h in range(NUM_HOURS - 1, -1, -1):
        for a in range(NUM_PARKS):
            Q[a][h] = reward[a][h] + V[h + 1]
        V[h] = np.max(Q[:, h])

    optimal = [int(np.argmax(Q[:, h])) + 1 for h in range(NUM_HOURS)]

    # Verify against latent recommendation in data
    latent = day_data.sort_values("hour")["latent_recommended_park_idx"].values + 1

    print(f"\nDay {day}  |  Optimal policy: {optimal}  |  Data latent: {list(latent.astype(int))}"
          f"  |  V*(s1) = {V[0]:.2f}")
    print(f"  {'':8s}  {'Hour 1':>8s}  {'Hour 2':>8s}  {'Hour 3':>8s}  {'Hour 4':>8s}  {'Hour 5':>8s}")
    for p in range(NUM_PARKS):
        vals = "  ".join(f"{Q[p][h]:8.2f}" for h in range(NUM_HOURS))
        print(f"  Park {p+1}    {vals}")
    print(f"  V*(h)   " + "  ".join(f"{V[h]:8.2f}" for h in range(NUM_HOURS)))


# ======================================================================
# 1b) DAY x HOUR CHOICE-PROBABILITY HEATMAPS
# ======================================================================
print("\n" + "=" * 70)
print("1b) DAY x HOUR CHOICE-PROBABILITY HEATMAPS")
print("=" * 70)

fig, axes = plt.subplots(3, 3, figsize=(15, 12), sharex=True, sharey=True)
axes = axes.flatten()
park_labels = [f"Park {p+1}" for p in range(NUM_PARKS)]
hour_labels = [f"Hour {h}" for h in range(1, NUM_HOURS + 1)]

for idx, day in enumerate(days):
    ax = axes[idx]
    day_sub = real[real["day"] == day]
    heatmap = np.zeros((NUM_PARKS, NUM_HOURS))

    for h in range(1, NUM_HOURS + 1):
        hour_sub = day_sub[day_sub["hour"] == h]
        if len(hour_sub) == 0:
            continue
        probs = (
            hour_sub["chosen_park_idx"]
            .value_counts(normalize=True)
            .reindex(range(NUM_PARKS), fill_value=0)
            .to_numpy()
        )
        heatmap[:, h - 1] = probs

    im = ax.imshow(heatmap, vmin=0, vmax=1, cmap="YlOrRd", aspect="auto")
    ax.grid(False)

    # Overlay the latent-optimal recommendation path for each hour.
    customers = np.zeros((NUM_PARKS, NUM_HOURS))
    trucks = np.zeros((NUM_PARKS, NUM_HOURS))
    for _, row in day_sub.drop_duplicates(subset=["hour"]).iterrows():
        h = int(row["hour"]) - 1
        customers[0][h] = row["park1_people"]
        customers[1][h] = row["park2_people"]
        customers[2][h] = row["park3_people"]
        trucks[0][h] = row["park1_trucks"]
        trucks[1][h] = row["park2_trucks"]
        trucks[2][h] = row["park3_trucks"]

    reward = np.divide(customers, trucks, out=np.zeros_like(customers, dtype=float), where=trucks > 0)
    Q = np.zeros((NUM_PARKS, NUM_HOURS))
    V = np.zeros(NUM_HOURS + 1)
    for h in range(NUM_HOURS - 1, -1, -1):
        for a in range(NUM_PARKS):
            Q[a][h] = reward[a][h] + V[h + 1]
        V[h] = np.max(Q[:, h])
    optimal = [int(np.argmax(Q[:, h])) for h in range(NUM_HOURS)]
    star_x = np.arange(NUM_HOURS) - 0.38
    star_y = np.array(optimal) - 0.38

    # Offset the markers so they sit near the cell corner rather than centered.
    ax.scatter(
        star_x,
        star_y,
        marker="*",
        s=220,
        facecolors="none",
        edgecolors="black",
        linewidths=1.4,
        zorder=5,
    )

    ax.set_title(f"Day {day}")
    ax.set_xticks(range(NUM_HOURS))
    ax.set_xticklabels(hour_labels, rotation=0)
    ax.set_yticks(range(NUM_PARKS))
    ax.set_yticklabels(park_labels)

    for p in range(NUM_PARKS):
        for h in range(NUM_HOURS):
            value = heatmap[p, h]
            ax.text(h, p, f"{value:.2f}", ha="center", va="center", fontsize=8,
                    color="white" if value >= 0.55 else "black")

for idx in range(len(days), len(axes)):
    axes[idx].axis("off")

fig.suptitle("Choice Probability by Day and Hour  (black stars = latent-optimal recommendation)", fontsize=16, y=0.98)
fig.subplots_adjust(left=0.06, right=0.88, bottom=0.06, top=0.93, wspace=0.25, hspace=0.35)
cbar_ax = fig.add_axes([0.905, 0.16, 0.02, 0.68])
fig.colorbar(im, cax=cbar_ax, label="P(chosen park | day, hour)")
fig.savefig(HEATMAP_PATH, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"Saved heatmap figure to {HEATMAP_PATH}")


# ======================================================================
# 2) BASELINE HUMAN POLICY (Days 1-2)
# ======================================================================
print("\n" + "=" * 70)
print("2) BASELINE HUMAN POLICY  π₀(park | hour)  [Days 1-2]")
print("=" * 70)

baseline = real[real["day"].isin([1, 2])]

print(f"\n  {'':8s}  {'Hour 1':>8s}  {'Hour 2':>8s}  {'Hour 3':>8s}  {'Hour 4':>8s}  {'Hour 5':>8s}")
for p in range(NUM_PARKS):
    probs = []
    for h in range(1, NUM_HOURS + 1):
        sub = baseline[baseline["hour"] == h]
        prob = (sub["chosen_park_idx"] == p).mean()
        probs.append(prob)
    print(f"  Park {p+1}  " + "  ".join(f"{pr:8.3f}" for pr in probs))

# Inertia check: P(stay at same park)
baseline_stay = baseline[baseline["previous_park_idx"].notna()].copy()
baseline_stay["stayed"] = (
    baseline_stay["chosen_park_idx"] == baseline_stay["previous_park_idx"].astype(float)
)
print(f"\n  Inertia (P(stay at same park) | hours 2-5): {baseline_stay['stayed'].mean():.3f}")

# Compare to random and optimal
print(f"  Baseline latent-optimal match rate:          {baseline['followed_latent_advice'].mean():.3f}")
print(f"  Random baseline (1/3):                       0.333")


# ======================================================================
# 3) COMPLIANCE BY FREQUENCY GROUP AND OVER TIME (Days 3-5, no social)
# ======================================================================
print("\n" + "=" * 70)
print("3) COMPLIANCE ANALYSIS — RECOMMENDATIONS ONLY (Days 3-5)")
print("=" * 70)

rec_phase = real[(real["day"] >= 3) & (real["day"] <= 5)]

# 3a. Compliance when advice IS shown, by frequency group
print("\n3a. P(follow advice | advice shown) by frequency group")
vis = rec_phase[rec_phase["had_visible_advice"] == True]
for freq in [1, 2, 3]:
    sub = vis[vis["advice_freq_assigned"] == freq]
    n = len(sub)
    rate = sub["followed_visible_advice"].mean()
    print(f"  {FREQ_LABELS[freq]:>4s} group:  {rate:.3f}  (n={n})")

# 3b. Compliance over time (by day)
print("\n3b. P(follow advice | advice shown) by day")
for day in [3, 4, 5]:
    sub = vis[vis["day"] == day]
    for freq in [1, 2, 3]:
        fsub = sub[sub["advice_freq_assigned"] == freq]
        rate = fsub["followed_visible_advice"].mean() if len(fsub) > 0 else float("nan")
        n = len(fsub)
        print(f"  Day {day}, {FREQ_LABELS[freq]:>4s}:  {rate:.3f}  (n={n})")

# 3c. Latent compliance (chose optimal WITHOUT seeing advice)
print("\n3c. Latent compliance (chose optimal when advice NOT shown) by freq group")
no_vis = rec_phase[rec_phase["had_visible_advice"] == False]
for freq in [1, 2, 3]:
    sub = no_vis[no_vis["advice_freq_assigned"] == freq]
    rate = sub["followed_latent_advice"].mean()
    print(f"  {FREQ_LABELS[freq]:>4s} group:  {rate:.3f}  (n={len(sub)})")

# 3d. Latent compliance over time
print("\n3d. Latent compliance by day (learning without seeing advice)")
for day in [3, 4, 5]:
    sub = no_vis[no_vis["day"] == day]
    rate = sub["followed_latent_advice"].mean()
    print(f"  Day {day}:  {rate:.3f}  (n={len(sub)})")

# 3e. Compliance by hour (are some hours easier to learn?)
print("\n3e. Compliance by hour (advice shown, days 3-5)")
for h in range(1, NUM_HOURS + 1):
    sub = vis[vis["hour"] == h]
    rate = sub["followed_visible_advice"].mean() if len(sub) > 0 else float("nan")
    print(f"  Hour {h}:  {rate:.3f}  (n={len(sub)})")


# ======================================================================
# 4) OPTIMAL RECOMMENDATION FREQUENCY
# ======================================================================
print("\n" + "=" * 70)
print("4) OPTIMAL RECOMMENDATION FREQUENCY (Days 3-5)")
print("=" * 70)

# 4a. Total reward by group
print("\n4a. Mean reward per round by frequency group")
for freq in [1, 2, 3]:
    sub = rec_phase[rec_phase["advice_freq_assigned"] == freq]
    print(f"  {FREQ_LABELS[freq]:>4s} group:  {sub['reward'].mean():.2f}")

# 4b. Reward WHEN advice shown vs NOT shown
print("\n4b. Reward when advice IS shown vs NOT shown")
print(f"  {'Group':>6s}  {'w/ advice':>10s}  {'w/o advice':>11s}  {'Δ':>7s}")
for freq in [1, 2, 3]:
    sub_vis = vis[vis["advice_freq_assigned"] == freq]
    sub_no = no_vis[no_vis["advice_freq_assigned"] == freq]
    r_vis = sub_vis["reward"].mean()
    r_no = sub_no["reward"].mean()
    print(f"  {FREQ_LABELS[freq]:>6s}  {r_vis:>10.2f}  {r_no:>11.2f}  {r_vis - r_no:>+7.2f}")

# 4c. Q*-based shortfall decomposition
print("\n4c. Mean per-step shortfall  V*(h) - Q*(h, chosen_action)")
for freq in [1, 2, 3]:
    sub = rec_phase[rec_phase["advice_freq_assigned"] == freq]
    shortfalls = []
    for _, row in sub.iterrows():
        day = int(row["day"])
        h = int(row["hour"]) - 1
        chosen = int(row["chosen_park_idx"])

        # Recompute Q for this day (cached would be better but clarity > speed)
        day_ref = real[(real["day"] == day)].drop_duplicates(subset=["hour"]).sort_values("hour")
        cust = np.zeros((NUM_PARKS, NUM_HOURS))
        trk = np.zeros((NUM_PARKS, NUM_HOURS))
        for _, rr in day_ref.iterrows():
            hh = int(rr["hour"]) - 1
            cust[0][hh], cust[1][hh], cust[2][hh] = rr["park1_people"], rr["park2_people"], rr["park3_people"]
            trk[0][hh], trk[1][hh], trk[2][hh] = rr["park1_trucks"], rr["park2_trucks"], rr["park3_trucks"]
        rwd = np.where(trk > 0, cust / trk, 0)
        Qd = np.zeros((NUM_PARKS, NUM_HOURS))
        Vd = np.zeros(NUM_HOURS + 1)
        for t in range(NUM_HOURS - 1, -1, -1):
            for a in range(NUM_PARKS):
                Qd[a][t] = rwd[a][t] + Vd[t + 1]
            Vd[t] = np.max(Qd[:, t])
        shortfalls.append(Vd[h] - Qd[chosen][h])
    print(f"  {FREQ_LABELS[freq]:>4s} group:  mean shortfall = {np.mean(shortfalls):.3f}  "
          f"(cumulative over 5h = {np.mean(shortfalls) * 5:.2f})")

# 4d. Learning transfer: performance in rounds WITHOUT advice
print("\n4d. Latent-optimal rate across days (learning transfer)")
print(f"  {'Day':>4s}  {'10%':>6s}  {'50%':>6s}  {'90%':>6s}")
for day in days:
    vals = []
    for freq in [1, 2, 3]:
        sub = real[(real["day"] == day) & (real["advice_freq_assigned"] == freq)
                   & (real["had_visible_advice"] == False)]
        vals.append(sub["followed_latent_advice"].mean() if len(sub) > 0 else float("nan"))
    print(f"  {day:>4d}  " + "  ".join(f"{v:>6.3f}" if not np.isnan(v) else f"{'n/a':>6s}" for v in vals))


# ======================================================================
# 5) SOCIAL INFORMATION ANALYSIS (Days 6-8)
# ======================================================================
print("\n" + "=" * 70)
print("5) SOCIAL INFORMATION ANALYSIS (Days 6-8)")
print("=" * 70)

social_phase = real[real["day"] >= 6]

# 5a. Compliance when advice shown, by social condition
print("\n5a. P(follow advice | advice shown) by social condition x freq")
vis_soc = social_phase[social_phase["had_visible_advice"] == True]
print(f"  {'':>6s}  {'agree':>8s}  {'against':>8s}")
for freq in [1, 2, 3]:
    vals = []
    for cond in ["agree", "against"]:
        sub = vis_soc[(vis_soc["advice_freq_assigned"] == freq)
                      & (vis_soc["social_condition_assigned"] == cond)]
        vals.append(sub["followed_visible_advice"].mean() if len(sub) > 0 else float("nan"))
    print(f"  {FREQ_LABELS[freq]:>6s}  " + "  ".join(f"{v:>8.3f}" for v in vals))

# 5b. Latent compliance by social condition
print("\n5b. Latent compliance (no advice shown) by social condition x freq")
no_vis_soc = social_phase[social_phase["had_visible_advice"] == False]
print(f"  {'':>6s}  {'agree':>8s}  {'against':>8s}")
for freq in [1, 2, 3]:
    vals = []
    for cond in ["agree", "against"]:
        sub = no_vis_soc[(no_vis_soc["advice_freq_assigned"] == freq)
                         & (no_vis_soc["social_condition_assigned"] == cond)]
        vals.append(sub["followed_latent_advice"].mean() if len(sub) > 0 else float("nan"))
    print(f"  {FREQ_LABELS[freq]:>6s}  " + "  ".join(f"{v:>8.3f}" for v in vals))

# 5c. Reward by social condition
print("\n5c. Mean reward per round by social condition x freq")
print(f"  {'':>6s}  {'agree':>8s}  {'against':>8s}")
for freq in [1, 2, 3]:
    vals = []
    for cond in ["agree", "against"]:
        sub = social_phase[(social_phase["advice_freq_assigned"] == freq)
                           & (social_phase["social_condition_assigned"] == cond)]
        vals.append(sub["reward"].mean())
    print(f"  {FREQ_LABELS[freq]:>6s}  " + "  ".join(f"{v:>8.2f}" for v in vals))

# 5d. Compare rec-only phase vs social phase (same people)
print("\n5d. Compliance change: rec-only (days 3-5) → social (days 6-8)")
print(f"  {'':>6s}  {'Rec only':>9s}  {'+ Social':>9s}  {'Δ':>7s}")
for freq in [1, 2, 3]:
    r1 = rec_phase[(rec_phase["advice_freq_assigned"] == freq)
                   & (rec_phase["had_visible_advice"] == True)]["followed_visible_advice"].mean()
    r2 = vis_soc[vis_soc["advice_freq_assigned"] == freq]["followed_visible_advice"].mean()
    print(f"  {FREQ_LABELS[freq]:>6s}  {r1:>9.3f}  {r2:>9.3f}  {r2 - r1:>+7.3f}")

# 5e. Does social info substitute for recommendations?
print("\n5e. Reward WITHOUT advice: rec-only vs social phase")
print(f"  {'':>6s}  {'Rec only':>9s}  {'+ Social':>9s}  {'Δ':>7s}")
for freq in [1, 2, 3]:
    sub_r = no_vis[no_vis["advice_freq_assigned"] == freq]
    sub_s = no_vis_soc[no_vis_soc["advice_freq_assigned"] == freq]
    r1 = sub_r["reward"].mean()
    r2 = sub_s["reward"].mean()
    print(f"  {FREQ_LABELS[freq]:>6s}  {r1:>9.2f}  {r2:>9.2f}  {r2 - r1:>+7.2f}")

# 5f. Social over time
print("\n5f. Latent compliance by day in social phase, by condition")
print(f"  {'Day':>4s}  {'agree':>8s}  {'against':>8s}")
for day in [6, 7, 8]:
    vals = []
    for cond in ["agree", "against"]:
        sub = no_vis_soc[(no_vis_soc["day"] == day)
                         & (no_vis_soc["social_condition_assigned"] == cond)]
        vals.append(sub["followed_latent_advice"].mean() if len(sub) > 0 else float("nan"))
    print(f"  {day:>4d}  " + "  ".join(f"{v:>8.3f}" for v in vals))


# ======================================================================
# 6) CI-BASED FIGURES FOR RECOMMENDATION, SOCIAL, AND EFFICIENCY ANALYSES
# ======================================================================
print("\n" + "=" * 70)
print("6) SAVING CI-BASED FIGURES")
print("=" * 70)

day_cache = build_day_value_cache(real)
rec_plot = rec_phase.copy()
rec_plot["shortfall"] = rec_plot.apply(lambda row: row_shortfall(row, day_cache), axis=1)
social_plot = social_phase.copy()
social_plot["shortfall"] = social_plot.apply(lambda row: row_shortfall(row, day_cache), axis=1)

freq_order = [1, 2, 3]
day_3_5_order = [3, 4, 5]
hour_order = [1, 2, 3, 4, 5]
social_order = ["agree", "against"]
freq_labels = [FREQ_LABELS[freq] for freq in freq_order]
freq_label_palette = {FREQ_LABELS[freq]: REC_COLORS[freq] for freq in freq_order}
social_labels = ["Agree", "Against"]
social_label_palette = {"Agree": SOCIAL_COLORS["agree"], "Against": SOCIAL_COLORS["against"]}

freq_palette = {freq: REC_COLORS[freq] for freq in freq_order}
social_palette = {cond: SOCIAL_COLORS[cond] for cond in social_order}

rec_visible_summary = summarize_binary(
    rec_plot[rec_plot["had_visible_advice"] == True],
    ["day", "advice_freq_assigned"],
    "followed_visible_advice",
)
rec_latent_summary = summarize_binary(
    rec_plot[rec_plot["had_visible_advice"] == False],
    ["day", "advice_freq_assigned"],
    "followed_latent_advice",
)
rec_reward_summary = summarize_numeric(rec_plot, ["day", "advice_freq_assigned"], "reward")
rec_shortfall_summary = summarize_numeric(rec_plot, ["day", "advice_freq_assigned"], "shortfall")

fig, axes = plt.subplots(2, 2, figsize=(13.5, 10), sharex=True)
plot_grouped_bars(
    axes[0, 0],
    rec_visible_summary,
    "day",
    day_3_5_order,
    hue_col="advice_freq_assigned",
    hue_order=freq_order,
    palette=freq_palette,
    ylabel="P(follow advice)",
    xlabel="Day",
    title="Visible compliance",
    legend_title="Recommendation",
    show_legend=False,
)
plot_grouped_bars(
    axes[0, 1],
    rec_latent_summary,
    "day",
    day_3_5_order,
    hue_col="advice_freq_assigned",
    hue_order=freq_order,
    palette=freq_palette,
    ylabel="P(choose latent optimum)",
    xlabel="Day",
    title="Latent compliance",
    legend_title="Recommendation",
    show_legend=False,
)
plot_grouped_bars(
    axes[1, 0],
    rec_reward_summary,
    "day",
    day_3_5_order,
    hue_col="advice_freq_assigned",
    hue_order=freq_order,
    palette=freq_palette,
    ylabel="Mean reward",
    xlabel="Day",
    title="Reward",
    legend_title="Recommendation",
    show_legend=False,
)
plot_grouped_bars(
    axes[1, 1],
    rec_shortfall_summary,
    "day",
    day_3_5_order,
    hue_col="advice_freq_assigned",
    hue_order=freq_order,
    palette=freq_palette,
    ylabel="Mean shortfall",
    xlabel="Day",
    title="Shortfall",
    legend_title="Recommendation",
    show_legend=False,
)
fig.suptitle("Days 3-5: Recommendation groups with confidence intervals", fontsize=16, y=0.98)
add_figure_legend(fig, freq_labels, freq_label_palette, "Recommendation group", ncol=3, anchor_y=0.01)
fig.tight_layout(rect=[0, 0.06, 1, 0.95])
save_figure(fig, RECOMMENDATION_CI_PATH)
print(f"Saved {RECOMMENDATION_CI_PATH.name}")

social_visible_summary = summarize_binary(
    social_plot[social_plot["had_visible_advice"] == True],
    ["social_condition_assigned", "advice_freq_assigned"],
    "followed_visible_advice",
)
social_latent_summary = summarize_binary(
    social_plot[social_plot["had_visible_advice"] == False],
    ["social_condition_assigned", "advice_freq_assigned"],
    "followed_latent_advice",
)
social_reward_summary = summarize_numeric(social_plot, ["social_condition_assigned", "advice_freq_assigned"], "reward")
social_shortfall_summary = summarize_numeric(social_plot, ["social_condition_assigned", "advice_freq_assigned"], "shortfall")

fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.5), sharex=True)
plot_grouped_bars(
    axes[0, 0],
    social_visible_summary,
    "social_condition_assigned",
    social_order,
    hue_col="advice_freq_assigned",
    hue_order=freq_order,
    palette=freq_palette,
    ylabel="P(follow advice)",
    xlabel="Social condition",
    title="Visible compliance",
    legend_title="Recommendation",
    show_legend=False,
)
plot_grouped_bars(
    axes[0, 1],
    social_latent_summary,
    "social_condition_assigned",
    social_order,
    hue_col="advice_freq_assigned",
    hue_order=freq_order,
    palette=freq_palette,
    ylabel="P(choose latent optimum)",
    xlabel="Social condition",
    title="Latent compliance",
    legend_title="Recommendation",
    show_legend=False,
)
plot_grouped_bars(
    axes[1, 0],
    social_reward_summary,
    "social_condition_assigned",
    social_order,
    hue_col="advice_freq_assigned",
    hue_order=freq_order,
    palette=freq_palette,
    ylabel="Mean reward",
    xlabel="Social condition",
    title="Reward",
    legend_title="Recommendation",
    show_legend=False,
)
plot_grouped_bars(
    axes[1, 1],
    social_shortfall_summary,
    "social_condition_assigned",
    social_order,
    hue_col="advice_freq_assigned",
    hue_order=freq_order,
    palette=freq_palette,
    ylabel="Mean shortfall",
    xlabel="Social condition",
    title="Shortfall",
    legend_title="Recommendation",
    show_legend=False,
)
fig.suptitle("Days 6-8: Social information x recommendation group with confidence intervals", fontsize=16, y=0.98)
add_figure_legend(fig, freq_labels, freq_label_palette, "Recommendation group", ncol=3, anchor_y=0.01)
fig.tight_layout(rect=[0, 0.06, 1, 0.95])
save_figure(fig, SOCIAL_CI_PATH)
print(f"Saved {SOCIAL_CI_PATH.name}")


# ======================================================================
# 8) THREE-MICROCLUSTER ANALYSIS FOR THE EFFICIENT GROUP
# ======================================================================
print("\n" + "=" * 70)
print("8) THREE-MICROCLUSTER ANALYSIS FOR THE EFFICIENT GROUP")
print("=" * 70)

import efficient_microcluster_analysis as micro_analysis

micro_summary = micro_analysis.load_all_participants()
micro_attempts = pd.read_csv(ATTEMPTS_PATH).copy()
micro_attempts["is_correct_int"] = pd.to_numeric(micro_attempts["is_correct_int"], errors="coerce")
micro_attempts["answer_duration_ms"] = pd.to_numeric(micro_attempts["answer_duration_ms"], errors="coerce")

efficient_group = micro_analysis.identify_efficient_group(micro_summary)
micro_features = micro_analysis.build_efficient_features(efficient_group, micro_attempts)
micro_matrix = micro_analysis.standardize_features(micro_features)

best_micro3 = None
for seed in range(30):
    labels, centroids, inertia = micro_analysis.run_kmeans(micro_matrix, 3, random_state=seed)
    score = micro_analysis.silhouette_score(micro_matrix, labels)
    candidate = micro_analysis.ClusterResult(
        k=3,
        labels=labels,
        centroids=centroids,
        inertia=inertia,
        silhouette=score,
    )
    if best_micro3 is None:
        best_micro3 = candidate
        continue
    if not np.isnan(candidate.silhouette) and (np.isnan(best_micro3.silhouette) or candidate.silhouette > best_micro3.silhouette):
        best_micro3 = candidate

micro_frame = efficient_group.copy()
for column in micro_features.columns:
    micro_frame[column] = micro_features[column].values
micro_frame["reward_per_round"] = micro_frame["total_reward"] / micro_frame["rounds_completed"]
micro_frame["microcluster_id"] = best_micro3.labels

micro_rank = (
    micro_frame.groupby("microcluster_id", as_index=False)["final_earnings"]
    .mean()
    .sort_values("final_earnings", ascending=False)
    .reset_index(drop=True)
)
micro_rank_map = {
    int(row["microcluster_id"]): f"Microcluster {rank + 1}"
    for rank, (_, row) in enumerate(micro_rank.iterrows())
}
micro_frame["microcluster_label"] = micro_frame["microcluster_id"].map(micro_rank_map)
micro_order = [micro_rank_map[int(cluster_id)] for cluster_id in micro_rank["microcluster_id"]]
micro_palette = {label: REC_COLORS[index + 1] for index, label in enumerate(micro_order)}

print(f"Efficient participants: {len(efficient_group)}")
print(f"k=3 silhouette: {best_micro3.silhouette:.3f}")
print(f"Cluster sizes: {micro_frame['microcluster_label'].value_counts().reindex(micro_order).to_dict()}")
micro_analysis.print_cluster_details(efficient_group, micro_features, best_micro3.labels)

micro_metrics = [
    ("final_earnings", "Final earnings"),
    ("reward_per_round", "Reward per round"),
    ("visible_advice_follow_rate", "Visible advice follow rate"),
    ("latent_advice_follow_rate", "Latent advice follow rate"),
    ("first_try_accuracy", "First-try accuracy"),
    ("retry_rate", "Retry rate"),
    ("learning_delta", "Learning delta"),
    ("avg_answer_duration_ms", "Avg answer duration (ms)"),
]

fig, axes = plt.subplots(2, 4, figsize=(18, 9.5), sharex=True)
for ax, (metric_col, metric_title) in zip(axes.flatten(), micro_metrics):
    metric_summary = summarize_numeric(micro_frame, ["microcluster_label"], metric_col)
    plot_grouped_bars(
        ax,
        metric_summary,
        "microcluster_label",
        micro_order,
        ylabel=metric_title,
        xlabel="Microcluster",
        title=metric_title,
        bar_colors=[micro_palette[label] for label in micro_order],
    )
    ax.tick_params(axis="x", rotation=0)

fig.suptitle(
    "Efficient group microclusters (k=3) with confidence intervals",
    fontsize=16,
    y=0.99,
)
fig.tight_layout(rect=[0, 0, 1, 0.95])
save_figure(fig, MICROCLUSTER_CI_PATH)
print(f"Saved {MICROCLUSTER_CI_PATH.name}")
print("\n" + "=" * 70)
print("Done.")
print("=" * 70)