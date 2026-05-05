"""
Baseline Policy Model
=====================
Constructs a model of baseline behavior (what people do without recommendations/social info)
using Day 2 data, then predicts and compares Days 3-8.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
import seaborn as sns
import json

from project_paths import data_file, ensure_results_dir

ROUND_PATH = data_file("foodtruck_clean_rounds.csv")
RESULTS_DIR = ensure_results_dir()

# Load data
rounds = pd.read_csv(ROUND_PATH)

print("=" * 70)
print("BASELINE POLICY MODEL: Day 2 → Days 3-8 Predictions")
print("=" * 70)

# ============================================================================
# STEP 1: Prepare Day 2 baseline data (no advice, no social)
# ============================================================================
print("\n[1] Building baseline model from Day 2 (no advice/social info)...")

day2 = rounds[rounds['day'] == 2].copy()
print(f"    Day 2 records: {len(day2)}")

# Create feature matrix: park metrics at decision time
# Features: person count, truck count, and computed ratio for each park
features_cols = ['park1_people', 'park1_trucks', 'park1_ratio', 'park1_workload',
                 'park2_people', 'park2_trucks', 'park2_ratio', 'park2_workload',
                 'park3_people', 'park3_trucks', 'park3_ratio', 'park3_workload']

# Target: which park was chosen (0, 1, or 2 for park indices)
# Using chosen_park_idx (0-indexed)

# Filter out rows with missing data
day2_clean = day2[features_cols + ['chosen_park_idx']].dropna()
print(f"    Valid records with complete features: {len(day2_clean)}")

X_train = day2_clean[features_cols].values
y_train = day2_clean['chosen_park_idx'].values

# Standardize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Train logistic regression model (one-vs-rest for 3-class classification)
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train_scaled, y_train)

train_acc = accuracy_score(y_train, model.predict(X_train_scaled))
print(f"    Baseline model accuracy (Day 2): {train_acc:.3f}")

# ============================================================================
# STEP 2: Predict Days 3-8 using the baseline model
# ============================================================================
print("\n[2] Applying baseline model to Days 3-8...")

days_3_8 = rounds[rounds['day'].isin([3, 4, 5, 6, 7, 8])].copy()
days_3_8_clean = days_3_8[features_cols + ['chosen_park_idx', 'day']].dropna()

X_test = days_3_8_clean[features_cols].values
y_test_actual = days_3_8_clean['chosen_park_idx'].values
X_test_scaled = scaler.transform(X_test)

y_test_pred = model.predict(X_test_scaled)
y_test_pred_proba = model.predict_proba(X_test_scaled)

overall_acc = accuracy_score(y_test_actual, y_test_pred)
print(f"    Baseline model accuracy (Days 3-8): {overall_acc:.3f}")

# ============================================================================
# STEP 3: Day-by-day comparison
# ============================================================================
print("\n[3] Day-by-day accuracy of baseline predictions:")
print("    Day | Accuracy | N Records")
print("    " + "-" * 35)

day_accuracies = []
for day in [3, 4, 5, 6, 7, 8]:
    day_mask = days_3_8_clean['day'].values == day
    if day_mask.sum() > 0:
        day_acc = accuracy_score(y_test_actual[day_mask], y_test_pred[day_mask])
        n_records = day_mask.sum()
        print(f"     {day}  |  {day_acc:.3f}   |  {n_records}")
        day_accuracies.append({'day': day, 'accuracy': day_acc, 'n': n_records})

day_acc_df = pd.DataFrame(day_accuracies)

# ============================================================================
# STEP 4: Analyze prediction mismatches (when baseline predicts wrong)
# ============================================================================
print("\n[4] Mismatch analysis (when baseline prediction != actual choice):")

mismatch_mask = y_test_pred != y_test_actual
print(f"    Total mismatches: {mismatch_mask.sum()} / {len(y_test_actual)} ({100*mismatch_mask.sum()/len(y_test_actual):.1f}%)")

days_3_8_clean['predicted_park_idx'] = y_test_pred
days_3_8_clean['is_mismatch'] = mismatch_mask

for day in [3, 4, 5, 6, 7, 8]:
    day_data = days_3_8_clean[days_3_8_clean['day'] == day]
    mismatch_count = (day_data['is_mismatch']).sum()
    mismatch_rate = 100 * mismatch_count / len(day_data)
    print(f"    Day {day}: {mismatch_count}/{len(day_data)} mismatches ({mismatch_rate:.1f}%)")

# ============================================================================
# STEP 5: Visualization
# ============================================================================
print("\n[5] Creating visualization...")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Baseline Policy Model: Day 2 → Days 3-8', fontsize=14, fontweight='bold')

# Plot 1: Accuracy by day
ax = axes[0, 0]
ax.bar(day_acc_df['day'], day_acc_df['accuracy'], color='#2F6DAE', alpha=0.7, edgecolor='black')
ax.axhline(y=train_acc, color='red', linestyle='--', label=f'Day 2 accuracy ({train_acc:.3f})', linewidth=2)
ax.set_xlabel('Day')
ax.set_ylabel('Prediction Accuracy')
ax.set_ylim([0, 1])
ax.set_title('Baseline Model Accuracy by Day')
ax.legend()
ax.grid(axis='y', alpha=0.3)

# Plot 2: Mismatch rate by day
ax = axes[0, 1]
mismatch_rates = []
for day in [3, 4, 5, 6, 7, 8]:
    day_data = days_3_8_clean[days_3_8_clean['day'] == day]
    mismatch_rate = 100 * (day_data['is_mismatch']).sum() / len(day_data)
    mismatch_rates.append(mismatch_rate)

colors = ['#D98E3A' if day <= 5 else '#B24C4C' for day in [3, 4, 5, 6, 7, 8]]
ax.bar([3, 4, 5, 6, 7, 8], mismatch_rates, color=colors, alpha=0.7, edgecolor='black')
ax.axvline(x=5.5, color='black', linestyle=':', alpha=0.5, linewidth=2)
ax.text(2, max(mismatch_rates)*0.95, 'Advice phase', fontsize=9, ha='left')
ax.text(6.5, max(mismatch_rates)*0.95, 'Social phase', fontsize=9, ha='left')
ax.set_xlabel('Day')
ax.set_ylabel('Mismatch Rate (%)')
ax.set_title('How Often Baseline Prediction ≠ Actual Choice')
ax.set_ylim([0, max(mismatch_rates)*1.15])
ax.grid(axis='y', alpha=0.3)

# Plot 3: Confusion matrix (Days 3-8 combined)
ax = axes[1, 0]
cm = confusion_matrix(y_test_actual, y_test_pred, labels=[0, 1, 2])
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax, cbar=False,
            xticklabels=['Park 1', 'Park 2', 'Park 3'],
            yticklabels=['Park 1', 'Park 2', 'Park 3'])
ax.set_ylabel('Actual Choice')
ax.set_xlabel('Baseline Prediction')
ax.set_title('Confusion Matrix (Days 3-8)')

# Plot 4: Cumulative accuracy
ax = axes[1, 1]
cumulative_correct = 0
cumulative_total = 0
cumulative_accuracies = []
for day in [3, 4, 5, 6, 7, 8]:
    day_mask = days_3_8_clean['day'].values == day
    cumulative_correct += (y_test_actual[day_mask] == y_test_pred[day_mask]).sum()
    cumulative_total += day_mask.sum()
    cumulative_accuracies.append(cumulative_correct / cumulative_total)

ax.plot([3, 4, 5, 6, 7, 8], cumulative_accuracies, marker='o', linewidth=2, markersize=8, color='#2F6DAE')
ax.axvline(x=5.5, color='black', linestyle=':', alpha=0.5, linewidth=2)
ax.fill_between([2.5, 5.5], 0, 1, alpha=0.1, color='#D98E3A', label='Advice phase')
ax.fill_between([5.5, 8.5], 0, 1, alpha=0.1, color='#B24C4C', label='Social phase')
ax.set_xlabel('Day')
ax.set_ylabel('Cumulative Accuracy')
ax.set_ylim([0, 1])
ax.set_title('Cumulative Model Accuracy Over Days 3-8')
ax.grid(alpha=0.3)
ax.legend(loc='lower right')

plt.tight_layout()
plt.savefig(RESULTS_DIR / 'baseline_model_predictions.png', dpi=220, bbox_inches='tight')
print(f"    Saved: baseline_model_predictions.png")
plt.close()

# ============================================================================
# STEP 6: Park-specific analysis
# ============================================================================
print("\n[5] Park-specific prediction patterns:")
print("\n    Park Choice Distribution:")
print("    " + "-" * 50)
print("    Park | Day2 Actual | Days3-8 Actual | Days3-8 Predicted")
print("    " + "-" * 50)

day2_park_dist = pd.Series(y_train).value_counts().sort_index()
for park_idx in [0, 1, 2]:
    day2_count = day2_park_dist.get(park_idx, 0)
    day2_pct = 100 * day2_count / len(y_train)
    
    actual_count = (y_test_actual == park_idx).sum()
    actual_pct = 100 * actual_count / len(y_test_actual)
    
    pred_count = (y_test_pred == park_idx).sum()
    pred_pct = 100 * pred_count / len(y_test_pred)
    
    print(f"     {park_idx+1}  | {day2_count:3d} ({day2_pct:5.1f}%) | {actual_count:3d} ({actual_pct:5.1f}%) | {pred_count:3d} ({pred_pct:5.1f}%)")

# ============================================================================
# Summary statistics
# ============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Baseline model trained on: Day 2 ({len(day2_clean)} records)")
print(f"Model predictions evaluated on: Days 3-8 ({len(days_3_8_clean)} records)")
print(f"\nOverall prediction accuracy (Days 3-8): {overall_acc:.3f}")
print(f"Total mismatches: {mismatch_mask.sum()}/{len(y_test_actual)} ({100*mismatch_mask.sum()/len(y_test_actual):.1f}%)")
print(f"\nInterpretation:")
print(f"  • Days 3-5 (Recommendation phase): Baseline predicts {day_acc_df[day_acc_df['day']<=5]['accuracy'].mean():.3f} (avg)")
print(f"  • Days 6-8 (Social phase): Baseline predicts {day_acc_df[day_acc_df['day']>5]['accuracy'].mean():.3f} (avg)")
print(f"\n  → The baseline model captures ~{overall_acc*100:.0f}% of Day 2 behavior")
print(f"  → In Days 3-8, people deviated from baseline ~{100*mismatch_mask.sum()/len(y_test_actual):.0f}% of the time")
print(f"  → This suggests recommendations/social info influenced choices significantly")
print("\n" + "=" * 70)

# Save detailed results
results_summary = {
    'baseline_day': 2,
    'baseline_train_accuracy': float(train_acc),
    'prediction_days': [3, 4, 5, 6, 7, 8],
    'overall_test_accuracy': float(overall_acc),
    'total_mismatches': int(mismatch_mask.sum()),
    'total_predictions': int(len(y_test_actual)),
    'mismatch_rate': float(mismatch_mask.sum() / len(y_test_actual)),
    'day_accuracies': [
        {'day': int(d['day']), 'accuracy': float(d['accuracy']), 'n': int(d['n'])}
        for d in day_accuracies
    ]
}

with open(RESULTS_DIR / 'baseline_model_results.json', 'w') as f:
    json.dump(results_summary, f, indent=2)
print("\nSaved detailed results to: baseline_model_results.json")
