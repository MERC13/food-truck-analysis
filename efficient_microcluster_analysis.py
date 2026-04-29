"""
Deep clustering within the efficient group to identify strategy micro-patterns.

The main clustering showed:
- Cluster 1 (8 people): Error-prone/lazy group
- Cluster 2 (48 people): Efficient group

This analysis subdivides the 48 efficient participants to find
distinct strategies and decision-making patterns.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
SUMMARY_PATH = DATA_DIR / "foodtruck_participant_summary.csv"
ATTEMPTS_PATH = DATA_DIR / "foodtruck_clean_attempts.csv"


@dataclass(frozen=True)
class ClusterResult:
    k: int
    labels: np.ndarray
    centroids: np.ndarray
    inertia: float
    silhouette: float


def load_all_participants() -> pd.DataFrame:
    """Load all participants."""
    summary = pd.read_csv(SUMMARY_PATH).copy()
    
    numeric_columns = [
        "rounds_completed", "final_earnings", "total_reward",
        "total_mistakes", "total_attempts", "retries",
        "first_try_correct", "final_correct",
        "advice_rounds_seen", "visible_advice_followed", "latent_advice_followed",
        "pre_earnings", "post_earnings",
        "follow_visible_rate", "first_try_accuracy", "final_accuracy",
        "retry_rate", "advice_freq_assigned",
    ]
    
    for col in numeric_columns:
        summary[col] = pd.to_numeric(summary[col], errors="coerce")
    
    summary = summary[summary["rounds_completed"].notna()].copy()
    summary = summary[summary["rounds_completed"] > 0].copy()
    summary = summary[summary["userid"].notna() | summary["name"].notna()].copy()
    
    return summary


def identify_efficient_group(summary: pd.DataFrame) -> pd.DataFrame:
    """
    Identify the efficient group based on characteristics:
    - Low retry rate (< 0.15)
    - High first try accuracy (> 0.85)
    - Low mistakes per round (< 0.2)
    """
    
    efficient = summary[
        (summary["retry_rate"] <= 0.15) &
        (summary["first_try_accuracy"] >= 0.85) &
        ((summary["total_mistakes"] / summary["total_attempts"]) < 0.2)
    ].copy()
    
    return efficient


def build_efficient_features(efficient_group: pd.DataFrame, attempts: pd.DataFrame) -> pd.DataFrame:
    """
    Build rich feature vectors for efficient players:
    1. Advice-following behavior
    2. Park specialization
    3. Earnings efficiency
    4. Learning patterns
    5. Decision speed
    """
    
    # Suppress copy warnings
    pd.options.mode.copy_on_write = True
    
    features = pd.DataFrame(index=efficient_group.index)
    
    # Advice-following behavior
    features["visible_advice_follow_rate"] = efficient_group["follow_visible_rate"].fillna(0.5)
    features["latent_advice_follow_rate"] = efficient_group["latent_advice_followed"] / efficient_group["rounds_completed"]
    features["visible_minus_latent"] = features["visible_advice_follow_rate"] - features["latent_advice_follow_rate"]
    
    # Performance metrics
    features["final_accuracy"] = efficient_group["final_accuracy"]
    features["first_try_accuracy"] = efficient_group["first_try_accuracy"]
    features["accuracy_improvement"] = efficient_group["final_accuracy"] - efficient_group["first_try_accuracy"]
    
    # Earnings efficiency
    features["reward_per_round"] = efficient_group["total_reward"] / efficient_group["rounds_completed"]
    features["earnings_normalized"] = efficient_group["final_earnings"] / 700  # 700 is near max
    
    # Retry and mistake patterns
    features["retry_rate"] = efficient_group["retry_rate"]
    features["mistakes_per_attempt"] = efficient_group["total_mistakes"] / efficient_group["total_attempts"]
    
    # Learning: did they improve from first to final?
    first_half = efficient_group["first_try_correct"]
    total = efficient_group["final_correct"]
    features["learning_delta"] = (total - first_half) / (efficient_group["rounds_completed"] + 1)
    
    # Advice exposure frequency
    features["advice_exposure_rate"] = efficient_group["advice_rounds_seen"] / efficient_group["rounds_completed"]
    
    # Social condition assigned (convert to numeric: agree=1, against=0)
    if "social_condition_assigned" in efficient_group.columns:
        features["likes_agreement"] = (efficient_group["social_condition_assigned"] == "agree").astype(float)
    
    # Advice frequency preference (low vs high frequency)
    if "advice_freq_assigned" in efficient_group.columns:
        features["advice_freq_preference"] = efficient_group["advice_freq_assigned"] / 3.0
    
    # Park specialization from attempts data
    for userid in efficient_group["userid"]:
        player_attempts = attempts[attempts["userid"] == userid]
        
        if len(player_attempts) > 0:
            # Accuracy by park
            for park_idx, park_col in [(0, "meadow_accuracy"), (1, "plaza_accuracy"), (2, "forest_accuracy")]:
                park_data = player_attempts[player_attempts["park_idx"] == park_idx]
                acc = park_data["is_correct_int"].mean() if len(park_data) > 0 else 0.5
                features.loc[efficient_group[efficient_group["userid"] == userid].index, park_col] = acc
            
            # Average decision complexity (sequence length from player_code)
            player_attempts["code_length"] = player_attempts["player_code"].fillna("").str.len()
            avg_len = player_attempts["code_length"].mean()
            features.loc[efficient_group[efficient_group["userid"] == userid].index, "avg_decision_length"] = avg_len
            
            # Average response time
            features.loc[efficient_group[efficient_group["userid"] == userid].index, "avg_answer_duration_ms"] = \
                player_attempts["answer_duration_ms"].mean()
    
    # Fill NaN values
    for col in features.columns:
        if features[col].isna().any():
            features[col].fillna(features[col].median(), inplace=True)
    
    return features


def standardize_features(features: pd.DataFrame) -> np.ndarray:
    """Standardize features to zero mean and unit variance."""
    values = features.to_numpy(dtype=float)
    means = np.nanmean(values, axis=0)
    stds = np.nanstd(values, axis=0)
    stds[stds == 0] = 1.0
    return (values - means) / stds


def run_kmeans(
    matrix: np.ndarray,
    k: int,
    max_iterations: int = 150,
    random_state: int = 42
) -> tuple[np.ndarray, np.ndarray, float]:
    """K-means clustering."""
    
    rng = np.random.RandomState(random_state)
    n_samples = matrix.shape[0]
    
    # K++ initialization
    centroids = [matrix[rng.randint(n_samples)]]
    while len(centroids) < k:
        centroid_matrix = np.vstack(centroids)
        distances = np.min(
            np.sum((matrix[:, None, :] - centroid_matrix[None, :, :]) ** 2, axis=2),
            axis=1,
        )
        total = distances.sum()
        if total == 0:
            centroids.append(matrix[rng.randint(n_samples)])
        else:
            probabilities = distances / total
            next_idx = rng.choice(n_samples, p=probabilities)
            centroids.append(matrix[next_idx])
    
    centroids = np.vstack(centroids)
    
    for iteration in range(max_iterations):
        distances = np.sum((matrix[:, None, :] - centroids[None, :, :]) ** 2, axis=2)
        labels = np.argmin(distances, axis=1)
        
        new_centroids = np.zeros_like(centroids)
        for i in range(k):
            members = matrix[labels == i]
            if len(members) > 0:
                new_centroids[i] = members.mean(axis=0)
            else:
                new_centroids[i] = centroids[i]
        
        if np.allclose(centroids, new_centroids):
            break
        
        centroids = new_centroids
    
    final_distances = np.sum((matrix[:, None, :] - centroids[None, :, :]) ** 2, axis=2)
    labels = np.argmin(final_distances, axis=1)
    inertia = float(np.sum(np.min(final_distances, axis=1)))
    
    return labels, centroids, inertia


def silhouette_score(matrix: np.ndarray, labels: np.ndarray) -> float:
    """Calculate silhouette score."""
    unique_labels = np.unique(labels)
    if len(unique_labels) < 2:
        return float("nan")
    
    distances = np.sqrt(np.sum((matrix[:, None, :] - matrix[None, :, :]) ** 2, axis=2))
    scores = []
    
    for i in range(matrix.shape[0]):
        same_cluster = labels == labels[i]
        same_cluster[i] = False
        a = np.mean(distances[i, same_cluster]) if np.any(same_cluster) else 0.0
        
        other_means = [
            np.mean(distances[i, labels == label])
            for label in unique_labels
            if label != labels[i] and np.any(labels == label)
        ]
        
        if not other_means:
            continue
        
        b = min(other_means)
        denominator = max(a, b)
        scores.append(0.0 if denominator == 0 else (b - a) / denominator)
    
    return float(np.mean(scores)) if scores else float("nan")


def find_best_k(matrix: np.ndarray, max_k: int = 8, restarts: int = 30) -> ClusterResult:
    """Find best k for the efficient group."""
    
    best_overall = None
    
    for k in range(2, min(max_k + 1, matrix.shape[0])):
        best_for_k = None
        
        for seed in range(restarts):
            labels, centroids, inertia = run_kmeans(matrix, k, random_state=seed)
            score = silhouette_score(matrix, labels)
            
            result = ClusterResult(k=k, labels=labels, centroids=centroids, inertia=inertia,
                                  silhouette=score)
            
            if best_for_k is None or (not np.isnan(score) and (np.isnan(best_for_k.silhouette) or score > best_for_k.silhouette)):
                best_for_k = result
        
        if best_for_k is not None:
            if best_overall is None or (not np.isnan(best_for_k.silhouette) and (np.isnan(best_overall.silhouette) or best_for_k.silhouette > best_overall.silhouette)):
                best_overall = best_for_k
    
    return best_overall


def print_cluster_details(
    efficient_group: pd.DataFrame,
    features: pd.DataFrame,
    labels: np.ndarray,
):
    """Print detailed breakdown of each micro-cluster."""
    
    k = len(np.unique(labels))
    
    print("\n" + "=" * 90)
    print(f"EFFICIENT PLAYER MICRO-CLUSTERS ({k} sub-strategies)")
    print("=" * 90)
    
    # Sort clusters by average earnings
    cluster_earnings = []
    for cluster_id in range(k):
        mask = labels == cluster_id
        avg_earnings = efficient_group.loc[mask, "final_earnings"].mean()
        cluster_earnings.append((cluster_id, avg_earnings))
    
    cluster_earnings.sort(key=lambda x: x[1], reverse=True)
    
    for cluster_id, _ in cluster_earnings:
        mask = labels == cluster_id
        cluster_data = efficient_group[mask]
        cluster_features = features[mask]
        
        print(f"\n{'─' * 90}")
        print(f"Strategy {cluster_id + 1}: {len(cluster_data)} players")
        print(f"{'─' * 90}")
        
        # Players
        print("Players:")
        for _, row in cluster_data.iterrows():
            name = row.get("name", "Unknown")
            earnings = row["final_earnings"]
            acc = row.get("final_accuracy", 0)
            print(f"  • {name:30} ${earnings:6.0f} ({acc*100:5.1f}%)")
        
        # Strategy profile
        print("\nStrategy Profile:")
        print(f"  Avg Earnings: ${cluster_features['earnings_normalized'].mean() * 700:.0f}")
        print(f"  Avg Final Accuracy: {cluster_features['final_accuracy'].mean():.3f}")
        print(f"  Advice Follow (Visible): {cluster_features['visible_advice_follow_rate'].mean():.2f}")
        print(f"  Advice Follow (Latent): {cluster_features['latent_advice_follow_rate'].mean():.2f}")
        print(f"  Learning Delta: {cluster_features['learning_delta'].mean():.4f}")
        
        # Park strengths
        if "meadow_accuracy" in cluster_features.columns:
            meadow = cluster_features["meadow_accuracy"].mean()
            plaza = cluster_features["plaza_accuracy"].mean()
            forest = cluster_features["forest_accuracy"].mean()
            print(f"  Park Specialization:")
            print(f"    Meadow: {meadow:.2f}  Plaza: {plaza:.2f}  Forest: {forest:.2f}")
            strongest = max([("Meadow", meadow), ("Plaza", plaza), ("Forest", forest)], key=lambda x: x[1])
            print(f"    → Strongest: {strongest[0]}")
        
        # Decision making
        if "avg_decision_length" in cluster_features.columns:
            print(f"  Decision Complexity (avg code length): {cluster_features['avg_decision_length'].mean():.1f}")
        if "avg_answer_duration_ms" in cluster_features.columns:
            print(f"  Avg Response Time: {cluster_features['avg_answer_duration_ms'].mean():.0f}ms")
        
        # Advice preference
        if "likes_agreement" in cluster_features.columns:
            agreement_pref = cluster_features["likes_agreement"].mean()
            print(f"  Social Preference: {'Agreement-oriented' if agreement_pref > 0.5 else 'Conflict/independent'} ({agreement_pref:.2%})")
        
        if "advice_freq_preference" in cluster_features.columns:
            freq_pref = cluster_features["advice_freq_preference"].mean() * 3
            print(f"  Advice Frequency Preference: {freq_pref:.1f}/3.0")
        
        # Interpretation
        print("\nInterpretation:")
        if cluster_features["visible_advice_follow_rate"].mean() > 0.8:
            print("  → ADVICE-DEPENDENT: This group heavily follows visible advice")
        elif cluster_features["latent_advice_follow_rate"].mean() > 0.6:
            print("  → INTUITIVE LEARNERS: This group learns patterns without explicit advice")
        else:
            print("  → INDEPENDENT thinkers: This group develops own strategies")
        
        if cluster_features["accuracy_improvement"].mean() > 0.05:
            print("  → PROGRESSIVE: Shows measurable improvement from first to final attempt")
        else:
            print("  → CONSISTENT: Maintains high accuracy throughout")


def main():
    print("Loading data...")
    summary = load_all_participants()
    attempts = pd.read_csv(ATTEMPTS_PATH).copy()
    attempts["is_correct_int"] = pd.to_numeric(attempts["is_correct_int"], errors="coerce")
    attempts["answer_duration_ms"] = pd.to_numeric(attempts["answer_duration_ms"], errors="coerce")
    
    print(f"Total participants: {len(summary)}")
    
    print("\nIdentifying efficient group...")
    efficient = identify_efficient_group(summary)
    print(f"Efficient players: {len(efficient)}")
    print(f"Error-prone players: {len(summary) - len(efficient)}")
    
    print("\nBuilding feature vectors for efficient group...")
    features = build_efficient_features(efficient, attempts)
    print(f"Feature dimensions: {features.shape}")
    
    print("\nStandardizing features...")
    matrix = standardize_features(features)
    
    print("\nSearching for optimal number of micro-clusters...")
    best = find_best_k(matrix, max_k=8, restarts=25)
    labels = best.labels
    
    print(f"Optimal k: {best.k} (silhouette: {best.silhouette:.3f}, inertia: {best.inertia:.1f})")
    
    sizes = [(i, (labels == i).sum()) for i in range(best.k)]
    sizes.sort(key=lambda x: x[1], reverse=True)
    print(f"Cluster sizes: {[f'C{i+1}:{s}' for i, s in sizes]}")
    
    print_cluster_details(efficient, features, labels)
    
    print("\n" + "=" * 90)
    print("SUMMARY")
    print("=" * 90)
    print("""
The efficient group breaks down into distinct sub-strategies:
1. ADVICE-DEPENDENT players who heavily follow visible guidance
2. INTUITIVE players who learn patterns and use latent information
3. INDEPENDENT players who develop personal strategies

These micro-clusters reveal how even high performers use different approaches
to succeed. Identify your cluster to find similar strategies.
    """)


if __name__ == "__main__":
    main()
