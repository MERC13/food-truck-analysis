"""Fast recommendation-policy analysis for the BobaLab study.

This version is designed to finish in seconds to a couple of minutes, not hours.
It uses grouped empirical summaries for frequency selection and a single learned
classifier for the state/history advice rule.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from project_paths import data_file


PHASE_DAYS = [3, 4, 5, 6, 7, 8]
FREQ_ORDER = [1, 2, 3]
FREQ_LABELS = {1: "10%", 2: "50%", 3: "90%"}
PRIOR_VISIBLE = 0.80
PRIOR_LATENT = 0.35


def load_rounds() -> pd.DataFrame:
    rounds = pd.read_csv(data_file("foodtruck_clean_rounds.csv")).copy()
    rounds = rounds[rounds["is_real_participant"] == True].copy()  # noqa: E712
    rounds = rounds[rounds["day"].isin(PHASE_DAYS)].copy()
    rounds = rounds.sort_values(["userid", "day", "hour"]).reset_index(drop=True)

    numeric_columns = [
        "reward",
        "previous_park_idx",
        "had_visible_advice_int",
        "followed_visible_advice_int",
        "followed_latent_advice_int",
        "park1_people",
        "park1_trucks",
        "park1_ratio",
        "park1_workload",
        "park2_people",
        "park2_trucks",
        "park2_ratio",
        "park2_workload",
        "park3_people",
        "park3_trucks",
        "park3_ratio",
        "park3_workload",
    ]

    for column in numeric_columns:
        rounds[column] = pd.to_numeric(rounds[column], errors="coerce")

    rounds["had_visible_advice_int"] = rounds["had_visible_advice_int"].fillna(0).astype(int)
    rounds["followed_visible_advice_int"] = pd.to_numeric(rounds["followed_visible_advice_int"], errors="coerce")
    rounds["followed_latent_advice_int"] = pd.to_numeric(rounds["followed_latent_advice_int"], errors="coerce")
    rounds["previous_park_idx"] = rounds["previous_park_idx"].fillna(-1)

    return rounds.dropna(subset=["reward"]).copy()


def build_history_features(rounds: pd.DataFrame) -> pd.DataFrame:
    df = rounds.copy()
    group = df.groupby("userid", sort=False)

    df["step_in_person"] = group.cumcount().astype(float)

    df["_visible_total"] = df["had_visible_advice_int"].astype(float)
    df["_latent_total"] = (1.0 - df["had_visible_advice_int"]).astype(float)
    df["_visible_success"] = df["_visible_total"] * df["followed_visible_advice_int"].fillna(0.0)
    df["_latent_success"] = df["_latent_total"] * df["followed_latent_advice_int"].fillna(0.0)

    past_visible_total = group["_visible_total"].cumsum() - df["_visible_total"]
    past_visible_success = group["_visible_success"].cumsum() - df["_visible_success"]
    past_latent_total = group["_latent_total"].cumsum() - df["_latent_total"]
    past_latent_success = group["_latent_success"].cumsum() - df["_latent_success"]
    past_advice_total = group["_visible_total"].cumsum() - df["_visible_total"]

    df["hist_visible_comp"] = (past_visible_success + PRIOR_VISIBLE) / (past_visible_total + 1.0)
    df["hist_latent_comp"] = (past_latent_success + PRIOR_LATENT) / (past_latent_total + 1.0)
    df["hist_advice_rate"] = (past_advice_total + 0.5) / (df["step_in_person"] + 1.0)
    df["hist_steps"] = df["step_in_person"]

    return df.drop(columns=["_visible_total", "_latent_total", "_visible_success", "_latent_success"])


def standardized_score(values: pd.Series) -> pd.Series:
    values = values.astype(float)
    std = values.std(ddof=0)
    if std == 0 or np.isnan(std):
        return values * 0.0
    return (values - values.mean()) / std


def summarize_frequency_policy(rounds: pd.DataFrame) -> pd.DataFrame:
    phase = rounds.copy()
    visible = phase[phase["had_visible_advice_int"] == 1].copy()
    latent = phase[phase["had_visible_advice_int"] == 0].copy()

    summary = pd.DataFrame(index=FREQ_ORDER)
    summary.index.name = "advice_freq_assigned"
    summary["mean_reward"] = phase.groupby("advice_freq_assigned")["reward"].mean()
    summary["visible_compliance"] = visible.groupby("advice_freq_assigned")["followed_visible_advice_int"].mean()
    summary["latent_compliance"] = latent.groupby("advice_freq_assigned")["followed_latent_advice_int"].mean()
    summary = summary.reindex(FREQ_ORDER)

    summary["reward_z"] = standardized_score(summary["mean_reward"])
    summary["latent_z"] = standardized_score(summary["latent_compliance"])
    summary["balanced_score"] = summary["reward_z"] + summary["latent_z"]
    return summary


def summarize_day_schedule(rounds: pd.DataFrame) -> pd.DataFrame:
    phase = rounds.copy()
    visible = phase[phase["had_visible_advice_int"] == 1].copy()
    latent = phase[phase["had_visible_advice_int"] == 0].copy()

    rows = []
    for day in PHASE_DAYS:
        day_phase = phase[phase["day"] == day]
        day_visible = visible[visible["day"] == day]
        day_latent = latent[latent["day"] == day]
        for freq in FREQ_ORDER:
            rows.append(
                {
                    "day": day,
                    "advice_freq_assigned": freq,
                    "mean_reward": day_phase[day_phase["advice_freq_assigned"] == freq]["reward"].mean(),
                    "visible_compliance": day_visible[day_visible["advice_freq_assigned"] == freq]["followed_visible_advice_int"].mean(),
                    "latent_compliance": day_latent[day_latent["advice_freq_assigned"] == freq]["followed_latent_advice_int"].mean(),
                }
            )

    summary = pd.DataFrame(rows)
    summary["reward_z"] = summary.groupby("day", group_keys=False)["mean_reward"].transform(standardized_score)
    summary["latent_z"] = summary.groupby("day", group_keys=False)["latent_compliance"].transform(standardized_score)
    summary["balanced_score"] = summary["reward_z"] + summary["latent_z"]
    return summary


def fit_advice_rule(rounds: pd.DataFrame):
    feature_columns = [
        "day",
        "hour",
        "previous_park_idx",
        "park1_people",
        "park1_trucks",
        "park1_ratio",
        "park1_workload",
        "park2_people",
        "park2_trucks",
        "park2_ratio",
        "park2_workload",
        "park3_people",
        "park3_trucks",
        "park3_ratio",
        "park3_workload",
        "hist_visible_comp",
        "hist_latent_comp",
        "hist_advice_rate",
        "hist_steps",
    ]

    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=2000, random_state=42),
    )
    X = rounds[feature_columns].fillna(rounds[feature_columns].median(numeric_only=True))
    y = rounds["had_visible_advice_int"].astype(int)
    model.fit(X, y)
    return model, feature_columns


def print_frequency_report(summary: pd.DataFrame, title: str) -> None:
    print("\n" + title)
    print("freq  reward   visible  latent   balanced")
    for freq in FREQ_ORDER:
        row = summary.loc[freq]
        print(
            f"{FREQ_LABELS[freq]:>4s}  "
            f"{row['mean_reward']:>6.3f}  "
            f"{row['visible_compliance']:>7.3f}  "
            f"{row['latent_compliance']:>6.3f}  "
            f"{row['balanced_score']:>8.3f}"
        )


def print_schedule_report(summary: pd.DataFrame, objective: str) -> None:
    print(f"\nBest day-by-day schedule ({objective}):")
    chosen = summary.loc[summary.groupby("day")[objective].idxmax()].sort_values("day")
    for _, row in chosen.iterrows():
        print(f"Day {int(row['day'])}: {FREQ_LABELS[int(row['advice_freq_assigned'])]}")


def describe_advice_rule(model, feature_columns: list[str], rounds: pd.DataFrame) -> None:
    sample = rounds[feature_columns].fillna(rounds[feature_columns].median(numeric_only=True)).iloc[[0]]
    prob = float(model.predict_proba(sample)[0, 1])

    logistic = model.named_steps["logisticregression"]
    scaler = model.named_steps["standardscaler"]
    coeffs = pd.Series(logistic.coef_[0], index=feature_columns)
    top_coeffs = coeffs.reindex(coeffs.abs().sort_values(ascending=False).index).head(6)

    print("\nAdvice decision rule")
    print("Predict advice probability from current state + history, then advise when p >= 0.5.")
    print(f"Example probability for the first analyzed row: {prob:.3f}")
    print("Most influential features in the fitted rule:")
    for name, value in top_coeffs.items():
        direction = "increases" if value > 0 else "decreases"
        print(f"  {name}: {direction} advice probability (coef={value:.3f})")


def main() -> None:
    rounds = build_history_features(load_rounds())

    print("=" * 78)
    print("Recommendation policy analysis")
    print("=" * 78)
    print(f"Rows analyzed: {len(rounds)}")
    print(f"Participants analyzed: {rounds['userid'].nunique()}")

    freq_summary = summarize_frequency_policy(rounds)
    print_frequency_report(freq_summary, "Fixed frequency summary")

    reward_best = int(freq_summary["mean_reward"].idxmax())
    latent_best = int(freq_summary["latent_compliance"].idxmax())
    balanced_best = int(freq_summary["balanced_score"].idxmax())

    print("\nBest fixed frequency")
    print(f"Reward-first: {FREQ_LABELS[reward_best]}")
    print(f"Learning-first: {FREQ_LABELS[latent_best]}")
    print(f"Balanced: {FREQ_LABELS[balanced_best]}")

    schedule_summary = summarize_day_schedule(rounds)
    print_schedule_report(schedule_summary, "balanced_score")

    model, feature_columns = fit_advice_rule(rounds)
    describe_advice_rule(model, feature_columns, rounds)

    print("\nDone.")


if __name__ == "__main__":
    main()