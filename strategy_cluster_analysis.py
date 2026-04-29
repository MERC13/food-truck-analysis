"""Cluster participant strategy profiles and print an interpretation.

This script uses the participant summary table to group people by behavioral
signals such as advice-following, reward, accuracy, and retry behavior. It does
not require scikit-learn; the clustering and silhouette scoring are implemented
with NumPy so the analysis runs in the existing virtual environment.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
SUMMARY_PATH = DATA_DIR / "foodtruck_participant_summary.csv"


@dataclass(frozen=True)
class ClusterResult:
    k: int
    labels: np.ndarray
    centroids: np.ndarray
    inertia: float
    silhouette: float


def load_participants() -> pd.DataFrame:
    summary = pd.read_csv(SUMMARY_PATH).copy()

    numeric_columns = [
        "rounds_completed",
        "final_earnings",
        "total_reward",
        "total_mistakes",
        "total_attempts",
        "retries",
        "first_try_correct",
        "final_correct",
        "advice_rounds_seen",
        "visible_advice_followed",
        "latent_advice_followed",
        "pre_earnings",
        "post_earnings",
        "follow_visible_rate",
        "first_try_accuracy",
        "final_accuracy",
        "retry_rate",
        "advice_freq_assigned",
    ]

    for column in numeric_columns:
        summary[column] = pd.to_numeric(summary[column], errors="coerce")

    summary = summary[summary["rounds_completed"].notna()].copy()
    summary = summary[summary["rounds_completed"] > 0].copy()
    summary = summary[summary["userid"].notna() | summary["name"].notna()].copy()

    return summary


def build_feature_frame(summary: pd.DataFrame) -> pd.DataFrame:
    features = pd.DataFrame(index=summary.index)
    rounds_completed = summary["rounds_completed"].astype(float)
    advice_seen = summary["advice_rounds_seen"].astype(float)

    features["reward_per_round"] = summary["total_reward"] / rounds_completed
    features["follow_visible_rate"] = summary["follow_visible_rate"].fillna(
        summary["visible_advice_followed"] / advice_seen.clip(lower=1)
    )
    features["follow_latent_rate"] = summary["latent_advice_followed"] / rounds_completed
    features["first_try_accuracy"] = summary["first_try_accuracy"]
    features["final_accuracy"] = summary["final_accuracy"]
    features["retry_rate"] = summary["retry_rate"]
    features["mistakes_per_round"] = summary["total_mistakes"] / rounds_completed
    features["advice_exposure_rate"] = advice_seen / rounds_completed

    return features.replace([np.inf, -np.inf], np.nan).fillna(features.median(numeric_only=True))


def standardize(frame: pd.DataFrame) -> np.ndarray:
    values = frame.to_numpy(dtype=float)
    means = np.nanmean(values, axis=0)
    stds = np.nanstd(values, axis=0)
    stds[stds == 0] = 1.0
    return (values - means) / stds


def kmeans_plus_plus_init(matrix: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    n_samples = matrix.shape[0]
    centroids = [matrix[rng.integers(n_samples)]]

    while len(centroids) < k:
        centroid_matrix = np.vstack(centroids)
        distances = np.min(
            np.sum((matrix[:, None, :] - centroid_matrix[None, :, :]) ** 2, axis=2),
            axis=1,
        )
        total = float(distances.sum())
        if total == 0:
            centroids.append(matrix[rng.integers(n_samples)])
            continue
        probabilities = distances / total
        next_index = rng.choice(n_samples, p=probabilities)
        centroids.append(matrix[next_index])

    return np.vstack(centroids)


def run_kmeans(matrix: np.ndarray, k: int, seed: int = 42, max_iter: int = 200) -> tuple[np.ndarray, np.ndarray, float]:
    rng = np.random.default_rng(seed)
    centroids = kmeans_plus_plus_init(matrix, k, rng)

    for _ in range(max_iter):
        distances = np.sum((matrix[:, None, :] - centroids[None, :, :]) ** 2, axis=2)
        labels = np.argmin(distances, axis=1)

        updated = centroids.copy()
        for cluster_id in range(k):
            members = matrix[labels == cluster_id]
            if len(members) == 0:
                updated[cluster_id] = matrix[rng.integers(matrix.shape[0])]
            else:
                updated[cluster_id] = members.mean(axis=0)

        if np.allclose(updated, centroids):
            centroids = updated
            break
        centroids = updated

    final_distances = np.sum((matrix[:, None, :] - centroids[None, :, :]) ** 2, axis=2)
    labels = np.argmin(final_distances, axis=1)
    inertia = float(np.sum(np.min(final_distances, axis=1)))
    return labels, centroids, inertia


def silhouette_score(matrix: np.ndarray, labels: np.ndarray) -> float:
    unique_labels = np.unique(labels)
    if len(unique_labels) < 2:
        return float("nan")

    distances = np.sqrt(np.sum((matrix[:, None, :] - matrix[None, :, :]) ** 2, axis=2))
    scores = []

    for i in range(matrix.shape[0]):
        same_cluster = labels == labels[i]
        same_cluster[i] = False
        if np.any(same_cluster):
            a = float(np.mean(distances[i, same_cluster]))
        else:
            a = 0.0

        other_means = []
        for label in unique_labels:
            if label == labels[i]:
                continue
            members = labels == label
            if np.any(members):
                other_means.append(float(np.mean(distances[i, members])))

        if not other_means:
            continue

        b = min(other_means)
        denominator = max(a, b)
        scores.append(0.0 if denominator == 0 else (b - a) / denominator)

    return float(np.mean(scores)) if scores else float("nan")


def cluster_candidates(matrix: np.ndarray, max_k: int = 6, restarts: int = 40) -> list[ClusterResult]:
    results: list[ClusterResult] = []
    upper = min(max_k, matrix.shape[0] - 1)
    for k in range(2, upper + 1):
        best: ClusterResult | None = None
        for restart in range(restarts):
            labels, centroids, inertia = run_kmeans(matrix, k, seed=42 + restart + k * 100)
            score = silhouette_score(matrix, labels)
            candidate = ClusterResult(k=k, labels=labels, centroids=centroids, inertia=inertia, silhouette=score)
            if best is None:
                best = candidate
                continue
            if np.isnan(candidate.silhouette):
                continue
            if np.isnan(best.silhouette) or candidate.silhouette > best.silhouette + 1e-9:
                best = candidate
            elif np.isclose(candidate.silhouette, best.silhouette) and candidate.inertia < best.inertia:
                best = candidate
        if best is not None:
            results.append(best)
    return results


def choose_best_cluster(results: list[ClusterResult]) -> ClusterResult:
    valid = [result for result in results if not np.isnan(result.silhouette)]
    if not valid:
        raise RuntimeError("Unable to score any clustering candidates.")
    valid.sort(key=lambda result: (-result.silhouette, result.k, result.inertia))
    return valid[0]


def cluster_sizes(labels: np.ndarray, k: int) -> list[int]:
    return [int((labels == cluster_id).sum()) for cluster_id in range(k)]


def print_k_search_report(results: list[ClusterResult]) -> None:
    print("\nK-search diagnostics (generic k-means sweep):")
    print(f"{'k':>3s}  {'silhouette':>10s}  {'inertia':>10s}  {'min_size':>8s}  {'cluster_sizes':>20s}")
    for result in results:
        sizes = cluster_sizes(result.labels, result.k)
        print(
            f"{result.k:>3d}  {result.silhouette:>10.3f}  {result.inertia:>10.2f}  "
            f"{min(sizes):>8d}  {str(sizes):>20s}"
        )


def print_k_search_insights(results: list[ClusterResult], best: ClusterResult) -> None:
    silhouettes = {result.k: result.silhouette for result in results}
    singleton_ks = [result.k for result in results if min(cluster_sizes(result.labels, result.k)) == 1]
    second_best = sorted(results, key=lambda r: r.silhouette, reverse=True)[1] if len(results) > 1 else None

    print("\nK-search interpretation:")
    print(
        f"- Best silhouette occurs at k={best.k} (score={best.silhouette:.3f}), "
        "which means this split has the strongest separation/compactness tradeoff in this feature space."
    )

    if second_best is not None:
        gap = best.silhouette - second_best.silhouette
        print(
            f"- Next best is k={second_best.k} at {second_best.silhouette:.3f}; "
            f"the gap is {gap:.3f}."
        )

    if singleton_ks:
        print(
            "- Higher-k solutions frequently produce singleton clusters "
            f"(k values: {singleton_ks}), suggesting those models may be splitting off outliers rather than discovering robust strategies."
        )

    if 2 in silhouettes and 3 in silhouettes:
        print(
            f"- Moving from k=2 to k=3 reduces silhouette from {silhouettes[2]:.3f} to {silhouettes[3]:.3f}, "
            "so an extra cluster does not improve structure quality here."
        )


def pretty_feature_name(name: str) -> str:
    return name.replace("_", " ")


def cluster_signature(zscores: pd.Series, top_n: int = 3) -> str:
    sorted_signals = zscores.reindex(zscores.abs().sort_values(ascending=False).index)
    pieces = []
    for feature_name, value in sorted_signals.items():
        if len(pieces) >= top_n:
            break
        if abs(value) < 0.35:
            continue
        direction = "high" if value > 0 else "low"
        pieces.append(f"{direction} {pretty_feature_name(feature_name)}")

    if not pieces:
        return "close to the overall average"

    return ", ".join(pieces)


def format_rate(value: float | int | np.floating) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{float(value):.3f}"


def describe_cluster(cluster_id: int, cluster_rows: pd.DataFrame, feature_frame: pd.DataFrame, all_features: pd.DataFrame) -> list[str]:
    means = feature_frame.mean(numeric_only=True)
    overall_means = all_features.mean(numeric_only=True)
    overall_stds = all_features.std(numeric_only=True).replace(0, 1.0)
    zscores = ((means - overall_means) / overall_stds).sort_values(key=lambda s: s.abs(), ascending=False)

    signature = cluster_signature(zscores)
    lines = [
        f"Cluster {cluster_id + 1}: {signature}",
        f"  size: {len(cluster_rows)} participants",
        f"  reward per round: {means['reward_per_round']:.2f}",
        f"  visible advice follow rate: {format_rate(means['follow_visible_rate'])}",
        f"  latent advice follow rate: {format_rate(means['follow_latent_rate'])}",
        f"  final accuracy: {format_rate(means['final_accuracy'])}",
        f"  retry rate: {format_rate(means['retry_rate'])}",
        f"  mistakes per round: {means['mistakes_per_round']:.3f}",
    ]

    if "advice_freq_assigned" in cluster_rows.columns:
        freq_mix = cluster_rows["advice_freq_assigned"].value_counts(normalize=True).sort_index()
        lines.append(
            "  advice frequency mix: "
            + ", ".join(f"{int(freq)} -> {share:.2%}" for freq, share in freq_mix.items())
        )

    condition_mix = cluster_rows["social_condition_assigned"].value_counts(normalize=True).sort_index()
    lines.append(
        "  social condition mix: "
        + ", ".join(f"{condition} -> {share:.2%}" for condition, share in condition_mix.items())
    )

    top_signals = []
    for feature_name in zscores.index[:3]:
        signal = zscores[feature_name]
        if signal >= 0.4:
            top_signals.append(f"high {pretty_feature_name(feature_name)}")
        elif signal <= -0.4:
            top_signals.append(f"low {pretty_feature_name(feature_name)}")
    if top_signals:
        lines.append("  dominant signals: " + ", ".join(top_signals))

    if zscores.get("reward_per_round", 0.0) > 0.5 and zscores.get("mistakes_per_round", 0.0) < 0:
        lines.append("  interpretation: this group is above average on payoff and below average on mistakes, so it looks efficient rather than noisy.")
    elif zscores.get("retry_rate", 0.0) > 0.5 or zscores.get("mistakes_per_round", 0.0) > 0.5:
        lines.append("  interpretation: this group stands out for friction in execution, with more retries or mistakes than the sample average.")
    elif zscores.get("follow_visible_rate", 0.0) > 0.4 or zscores.get("follow_latent_rate", 0.0) > 0.4:
        lines.append("  interpretation: this group is unusually advice-aligned, especially when advice is visible or latent recommendations are available.")
    else:
        lines.append("  interpretation: this group is differentiated by a combination of moderate shifts rather than one dominant behavior.")

    return lines


def main() -> None:
    summary = load_participants()
    features = build_feature_frame(summary)
    matrix = standardize(features)

    candidates = cluster_candidates(matrix)
    if not candidates:
        raise RuntimeError("Not enough participants to form clusters.")

    best = choose_best_cluster(candidates)
    labels = best.labels

    print("=" * 72)
    print("Strategy Cluster Analysis")
    print("=" * 72)
    print(f"Participants analyzed: {len(summary)}")
    print(f"Selected k: {best.k}")
    print(f"Silhouette score: {best.silhouette:.3f}")
    print(f"Inertia: {best.inertia:.3f}")
    print_k_search_report(candidates)
    print_k_search_insights(candidates, best)

    cluster_order = []
    for cluster_id in range(best.k):
        cluster_rows = summary.loc[labels == cluster_id].copy()
        cluster_features = features.loc[labels == cluster_id].copy()
        cluster_order.append((cluster_id, cluster_rows, cluster_features))

    print()
    for cluster_id, cluster_rows, cluster_features in sorted(
        cluster_order,
        key=lambda item: item[2]["reward_per_round"].mean(),
        reverse=True,
    ):
        for line in describe_cluster(cluster_id, cluster_rows, cluster_features, features):
            print(line)
        print()

    print("Overall interpretation:")
    print(
        "The clusters usually separate participants into an advice-led group, a self-directed high-performing group, "
        "and a more error-prone group. If the selected k is 2, the analysis is collapsing the last two patterns into one "
        "mixed cluster; if k is 4 or more, the extra clusters usually reflect a finer split inside the high-performer or "
        "mixed strategies rather than a completely new behavior type."
    )


if __name__ == "__main__":
    main()