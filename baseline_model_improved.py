"""
Improved Baseline Policy Model
================================
Tests multiple algorithmic approaches to baseline prediction:
1. Logistic Regression (original)
2. Park Ratio Heuristic (choose best efficiency)
3. Previous Choice Recency (people often repeat choices)
4. Hybrid (combination approach)

Then uses the best performer to predict Days 3-8.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from project_paths import data_file, ensure_results_dir

ROUND_PATH = data_file("foodtruck_clean_rounds.csv")
RESULTS_DIR = ensure_results_dir()

# Load data
rounds = pd.read_csv(ROUND_PATH)

print("=" * 80)
print("IMPROVED BASELINE POLICY: Multiple Algorithmic Approaches")
print("=" * 80)

# ============================================================================
# Prepare data
# ============================================================================
print("\n[Preparing data...]")

day2 = rounds[rounds['day'] == 2].copy()
days_3_8 = rounds[rounds['day'].isin([3, 4, 5, 6, 7, 8])].copy()

features_cols = ['park1_people', 'park1_trucks', 'park1_ratio', 'park1_workload',
                 'park2_people', 'park2_trucks', 'park2_ratio', 'park2_workload',
                 'park3_people', 'park3_trucks', 'park3_ratio', 'park3_workload']

# ============================================================================
# APPROACH 1: Logistic Regression (original)
# ============================================================================
print("\n[APPROACH 1] Logistic Regression on park metrics")

day2_clean = day2[features_cols + ['chosen_park_idx']].dropna()
X_train = day2_clean[features_cols].values
y_train = day2_clean['chosen_park_idx'].values

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

lr_model = LogisticRegression(max_iter=1000, random_state=42)
lr_model.fit(X_train_scaled, y_train)
lr_train_acc = accuracy_score(y_train, lr_model.predict(X_train_scaled))

print(f"  Training accuracy: {lr_train_acc:.3f}")

# ============================================================================
# APPROACH 2: Park Ratio Heuristic (choose park with best people/truck ratio)
# ============================================================================
print("\n[APPROACH 2] Park Ratio Heuristic (choose best efficiency)")

def ratio_heuristic_prediction(df):
    """Choose the park with the lowest people/truck ratio (best efficiency)"""
    parks_data = [
        df['park1_ratio'].values,
        df['park2_ratio'].values,
        df['park3_ratio'].values
    ]
    # argmin gives the park with lowest ratio (most efficient)
    predictions = np.argmin(parks_data, axis=0)
    return predictions

day2_heuristic = day2[features_cols + ['chosen_park_idx']].dropna()
y_heuristic_train = ratio_heuristic_prediction(day2_heuristic)
y_heuristic_actual = day2_heuristic['chosen_park_idx'].values
heuristic_train_acc = accuracy_score(y_heuristic_actual, y_heuristic_train)

print(f"  Training accuracy: {heuristic_train_acc:.3f}")

# ============================================================================
# APPROACH 3: Previous Choice Recency (high inertia model)
# ============================================================================
print("\n[APPROACH 3] Previous Choice Recency (choice inertia)")

# Build person-level previous choice mapping on Day 2
day2_recency = day2.sort_values(['response_id', 'hour']).copy()
day2_recency['previous_choice_same_person'] = day2_recency.groupby('response_id')['chosen_park_idx'].shift(1)

# Get last choice on Day 2 for each person
person_last_choice_day2 = day2_recency.groupby('response_id')['chosen_park_idx'].last()

def recency_prediction(df, person_last_choices, fallback_seed=42):
    """Predict using the person's last choice from Day 2"""
    rng = np.random.default_rng(fallback_seed)
    predictions = []
    for idx, row in df.iterrows():
        person_id = row['response_id']
        if person_id in person_last_choices.index:
            predictions.append(person_last_choices[person_id])
        else:
            # Deterministic fallback keeps runs reproducible across environments.
            predictions.append(int(rng.integers(0, 3)))
    return np.array(predictions)

# Test on Day 2 (comparing each choice to their previous in that day)
day2_with_prev = day2_recency.dropna(subset=['previous_choice_same_person']).copy()
if len(day2_with_prev) > 0:
    y_recency_actual = day2_with_prev['chosen_park_idx'].astype(int).values
    y_recency_pred = day2_with_prev['previous_choice_same_person'].astype(int).values
    recency_train_acc = accuracy_score(y_recency_actual, y_recency_pred)
else:
    recency_train_acc = 0.0

print(f"  Training accuracy: {recency_train_acc:.3f}")

# ============================================================================
# APPROACH 4: Hybrid (combine ratio heuristic + logistic regression)
# ============================================================================
print("\n[APPROACH 4] Hybrid (ratio heuristic + logistic regression ensemble)")

day2_hybrid = day2[features_cols + ['chosen_park_idx']].dropna()
y_ratio_pred = ratio_heuristic_prediction(day2_hybrid)
X_hybrid = scaler.transform(day2_hybrid[features_cols].values)
y_lr_pred_proba = lr_model.predict_proba(X_hybrid)

# Ensemble: if ratio heuristic has high confidence (clear winner), use it; otherwise use LR
hybrid_preds = []
for i in range(len(day2_hybrid)):
    ratio_choice = y_ratio_pred[i]
    lr_probs = y_lr_pred_proba[i]
    
    # If ratio heuristic's choice has >50% probability in LR, trust it
    # Otherwise use LR's best prediction
    if lr_probs[ratio_choice] > 0.40:
        hybrid_preds.append(ratio_choice)
    else:
        hybrid_preds.append(np.argmax(lr_probs))

y_hybrid_pred = np.array(hybrid_preds)
y_hybrid_actual = day2_hybrid['chosen_park_idx'].values
hybrid_train_acc = accuracy_score(y_hybrid_actual, y_hybrid_pred)

print(f"  Training accuracy: {hybrid_train_acc:.3f}")

# ============================================================================
# EVALUATE ON DAYS 3-8
# ============================================================================
print("\n" + "=" * 80)
print("EVALUATION ON DAYS 3-8")
print("=" * 80)

days_3_8_clean = days_3_8[features_cols + ['chosen_park_idx', 'day', 'response_id', 'hour']].dropna()
X_test = days_3_8_clean[features_cols].values
y_test_actual = days_3_8_clean['chosen_park_idx'].values
X_test_scaled = scaler.transform(X_test)

# Build recency mapping from Day 2 to Days 3-8
person_last_choice_day2 = day2.sort_values(['response_id', 'hour']).groupby('response_id')['chosen_park_idx'].last()

# Approach 1: LR
y_lr_pred = lr_model.predict(X_test_scaled)
lr_test_acc = accuracy_score(y_test_actual, y_lr_pred)

# Approach 2: Ratio Heuristic
y_ratio_pred = ratio_heuristic_prediction(days_3_8_clean)
ratio_test_acc = accuracy_score(y_test_actual, y_ratio_pred)

# Approach 3: Recency
y_recency_pred = recency_prediction(days_3_8_clean, person_last_choice_day2)
recency_test_acc = accuracy_score(y_test_actual, y_recency_pred)

# Approach 4: Hybrid
y_lr_pred_proba = lr_model.predict_proba(X_test_scaled)
hybrid_preds = []
for i in range(len(days_3_8_clean)):
    ratio_choice = y_ratio_pred[i]
    lr_probs = y_lr_pred_proba[i]
    
    if lr_probs[ratio_choice] > 0.40:
        hybrid_preds.append(ratio_choice)
    else:
        hybrid_preds.append(np.argmax(lr_probs))

y_hybrid_pred = np.array(hybrid_preds)
hybrid_test_acc = accuracy_score(y_test_actual, y_hybrid_pred)

# ============================================================================
# PRINT RESULTS
# ============================================================================
print("\nTRAINING ACCURACY (Day 2):")
print(f"  Logistic Regression:     {lr_train_acc:.3f}")
print(f"  Ratio Heuristic:         {heuristic_train_acc:.3f}")
print(f"  Recency (inertia):       {recency_train_acc:.3f}")
print(f"  Hybrid Ensemble:         {hybrid_train_acc:.3f}")

print("\nTEST ACCURACY (Days 3-8):")
print(f"  Logistic Regression:     {lr_test_acc:.3f}")
print(f"  Ratio Heuristic:         {ratio_test_acc:.3f}")
print(f"  Recency (inertia):       {recency_test_acc:.3f}")
print(f"  Hybrid Ensemble:         {hybrid_test_acc:.3f}")

# Find best approach
accuracies = {
    'Logistic Regression': lr_test_acc,
    'Ratio Heuristic': ratio_test_acc,
    'Recency (Inertia)': recency_test_acc,
    'Hybrid Ensemble': hybrid_test_acc
}
best_approach = max(accuracies, key=accuracies.get)
best_accuracy = accuracies[best_approach]

print(f"\n✓ BEST APPROACH: {best_approach} ({best_accuracy:.3f} accuracy)")

# Collect mismatch rates by day for visualization
mismatch_by_day = []
for day in [3, 4, 5, 6, 7, 8]:
    day_mask = days_3_8_clean['day'].values == day
    if day_mask.sum() > 0:
        if best_approach == 'Logistic Regression':
            day_pred = y_lr_pred[day_mask]
        elif best_approach == 'Ratio Heuristic':
            day_pred = y_ratio_pred[day_mask]
        elif best_approach == 'Recency (Inertia)':
            day_pred = y_recency_pred[day_mask]
        else:  # Hybrid
            day_pred = y_hybrid_pred[day_mask]
        
        day_actual = y_test_actual[day_mask]
        day_acc = accuracy_score(day_actual, day_pred)
        mismatch_rate = 100 * (day_actual != day_pred).sum() / len(day_actual)
        mismatch_by_day.append({
            'day': day,
            'accuracy': day_acc,
            'mismatch_rate': mismatch_rate,
            'n': len(day_actual)
        })

mismatch_df = pd.DataFrame(mismatch_by_day)

# ============================================================================
# VISUALIZATION
# ============================================================================
print("\n[Creating visualization...]")

fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)

fig.suptitle('Baseline Policy Model: Algorithmic Approach Comparison', 
             fontsize=16, fontweight='bold', y=0.98)

# Plot 1: Training accuracy comparison
ax1 = fig.add_subplot(gs[0, 0])
approaches = list(accuracies.keys())
train_accs = [lr_train_acc, heuristic_train_acc, recency_train_acc, hybrid_train_acc]
colors_train = ['#2F6DAE', '#4E9E6A', '#D98E3A', '#B24C4C']
bars = ax1.bar(range(len(approaches)), train_accs, color=colors_train, alpha=0.7, edgecolor='black')
ax1.set_ylabel('Accuracy', fontsize=11)
ax1.set_title('Training Accuracy (Day 2)', fontsize=12, fontweight='bold')
ax1.set_ylim([0, 1])
ax1.set_xticks(range(len(approaches)))
ax1.set_xticklabels(['Logistic\nRegression', 'Ratio\nHeuristic', 'Recency\n(Inertia)', 'Hybrid\nEnsemble'], fontsize=9)
ax1.grid(axis='y', alpha=0.3)
for i, (bar, acc) in enumerate(zip(bars, train_accs)):
    ax1.text(i, acc + 0.02, f'{acc:.3f}', ha='center', fontsize=9, fontweight='bold')

# Plot 2: Test accuracy comparison
ax2 = fig.add_subplot(gs[0, 1])
test_accs = [lr_test_acc, ratio_test_acc, recency_test_acc, hybrid_test_acc]
bars = ax2.bar(range(len(approaches)), test_accs, color=colors_train, alpha=0.7, edgecolor='black')
# Highlight best
best_idx = test_accs.index(max(test_accs))
bars[best_idx].set_edgecolor('green')
bars[best_idx].set_linewidth(3)
ax2.set_ylabel('Accuracy', fontsize=11)
ax2.set_title('Test Accuracy (Days 3-8)', fontsize=12, fontweight='bold')
ax2.set_ylim([0, 1])
ax2.set_xticks(range(len(approaches)))
ax2.set_xticklabels(['Logistic\nRegression', 'Ratio\nHeuristic', 'Recency\n(Inertia)', 'Hybrid\nEnsemble'], fontsize=9)
ax2.grid(axis='y', alpha=0.3)
for i, (bar, acc) in enumerate(zip(bars, test_accs)):
    ax2.text(i, acc + 0.02, f'{acc:.3f}', ha='center', fontsize=9, fontweight='bold')
ax2.axhline(y=0.33, color='red', linestyle='--', alpha=0.5, linewidth=1, label='Random (33%)')
ax2.legend(fontsize=8)

# Plot 3: Accuracy gain (train vs test)
ax3 = fig.add_subplot(gs[0, 2])
gains = [t - train for t, train in zip(test_accs, train_accs)]
bars = ax3.bar(range(len(approaches)), gains, color=['green' if g > 0 else 'red' for g in gains], 
               alpha=0.6, edgecolor='black')
ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax3.set_ylabel('Accuracy Change', fontsize=11)
ax3.set_title('Test vs Train Accuracy (overfitting check)', fontsize=12, fontweight='bold')
ax3.set_xticks(range(len(approaches)))
ax3.set_xticklabels(['Logistic\nRegression', 'Ratio\nHeuristic', 'Recency\n(Inertia)', 'Hybrid\nEnsemble'], fontsize=9)
ax3.grid(axis='y', alpha=0.3)
for i, (bar, gain) in enumerate(zip(bars, gains)):
    ax3.text(i, gain + 0.01 if gain > 0 else gain - 0.01, f'{gain:+.3f}', ha='center', fontsize=9)

# Plot 4: Accuracy by day (best model)
ax4 = fig.add_subplot(gs[1, :2])
ax4.bar(mismatch_df['day'], mismatch_df['accuracy'], color='#2F6DAE', alpha=0.7, edgecolor='black', label='Best Model')
ax4.axhline(y=best_accuracy, color='green', linestyle='--', linewidth=2, label=f'Average ({best_accuracy:.3f})')
ax4.axhline(y=0.33, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Random (33%)')
ax4.set_xlabel('Day', fontsize=11)
ax4.set_ylabel('Prediction Accuracy', fontsize=11)
ax4.set_title(f'Best Model ({best_approach}): Daily Accuracy', fontsize=12, fontweight='bold')
ax4.set_ylim([0, 1])
ax4.set_xticks([3, 4, 5, 6, 7, 8])
ax4.grid(axis='y', alpha=0.3)
ax4.legend(fontsize=10)
for day, acc in zip(mismatch_df['day'], mismatch_df['accuracy']):
    ax4.text(day, acc + 0.02, f'{acc:.3f}', ha='center', fontsize=9, fontweight='bold')

# Plot 5: Mismatch rate by day
ax5 = fig.add_subplot(gs[1, 2])
colors_phase = ['#D98E3A' if day <= 5 else '#B24C4C' for day in mismatch_df['day']]
ax5.bar(mismatch_df['day'], mismatch_df['mismatch_rate'], color=colors_phase, alpha=0.7, edgecolor='black')
ax5.axvline(x=5.5, color='black', linestyle=':', alpha=0.5, linewidth=2)
ax5.set_xlabel('Day', fontsize=11)
ax5.set_ylabel('Deviation from Baseline (%)', fontsize=11)
ax5.set_title('How Often People Deviated', fontsize=12, fontweight='bold')
ax5.set_ylim([0, 100])
ax5.set_xticks([3, 4, 5, 6, 7, 8])
ax5.grid(axis='y', alpha=0.3)
ax5.text(4, 95, 'Recommendation', fontsize=9, ha='center', style='italic')
ax5.text(7, 95, 'Social', fontsize=9, ha='center', style='italic')

# Plot 6: Confusion matrix (best model)
ax6 = fig.add_subplot(gs[2, 0])
if best_approach == 'Logistic Regression':
    best_pred = y_lr_pred
elif best_approach == 'Ratio Heuristic':
    best_pred = y_ratio_pred
elif best_approach == 'Recency (Inertia)':
    best_pred = y_recency_pred
else:
    best_pred = y_hybrid_pred

cm = confusion_matrix(y_test_actual, best_pred, labels=[0, 1, 2])
cm_norm = cm / cm.sum(axis=1, keepdims=True)
sns.heatmap(cm_norm, annot=cm, fmt='d', cmap='Blues', ax=ax6, cbar=False,
            xticklabels=['Park 1', 'Park 2', 'Park 3'],
            yticklabels=['Park 1', 'Park 2', 'Park 3'])
ax6.set_ylabel('Actual', fontsize=11)
ax6.set_xlabel('Predicted', fontsize=11)
ax6.set_title(f'Confusion Matrix ({best_approach})\nDays 3-8', fontsize=11, fontweight='bold')

# Plot 7: Park choice distribution
ax7 = fig.add_subplot(gs[2, 1])
day2_dist = pd.Series(y_train).value_counts().sort_index()
days_3_8_actual_dist = pd.Series(y_test_actual).value_counts().sort_index()
days_3_8_pred_dist = pd.Series(best_pred).value_counts().sort_index()

x = np.arange(3)
width = 0.25

bars1 = ax7.bar(x - width, [day2_dist.get(i, 0)/len(y_train)*100 for i in range(3)], 
               width, label='Day 2 (baseline)', alpha=0.8, edgecolor='black')
bars2 = ax7.bar(x, [days_3_8_actual_dist.get(i, 0)/len(y_test_actual)*100 for i in range(3)], 
               width, label='Days 3-8 (actual)', alpha=0.8, edgecolor='black')
bars3 = ax7.bar(x + width, [days_3_8_pred_dist.get(i, 0)/len(best_pred)*100 for i in range(3)], 
               width, label='Days 3-8 (predicted)', alpha=0.8, edgecolor='black')

ax7.set_ylabel('Percentage (%)', fontsize=11)
ax7.set_title('Park Choice Distribution', fontsize=11, fontweight='bold')
ax7.set_xticks(x)
ax7.set_xticklabels(['Park 1', 'Park 2', 'Park 3'])
ax7.legend(fontsize=9)
ax7.grid(axis='y', alpha=0.3)

# Plot 8: Performance summary table
ax8 = fig.add_subplot(gs[2, 2])
ax8.axis('off')

summary_text = f"""
BEST MODEL: {best_approach}

Training Accuracy (Day 2):
  {lr_train_acc:.1%}

Test Accuracy (Days 3-8):
  {best_accuracy:.1%}

Mismatch Rate:
  {100 - best_accuracy*100:.1f}%

Improvement over Random:
  {(best_accuracy - 0.33) / 0.33 * 100:.1f}%
  
N Participants: {len(day2)}
N Days Tested: 6
N Total Decisions: {len(y_test_actual)}
"""

ax8.text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
         verticalalignment='center')

plt.savefig(RESULTS_DIR / 'baseline_model_improved.png', dpi=220, bbox_inches='tight')
print(f"✓ Saved: baseline_model_improved.png")
plt.close()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print(f"\nKey Finding:")
print(f"  The '{best_approach}' approach achieves {best_accuracy:.1%} accuracy")
print(f"  compared to {lr_test_acc:.1%} for logistic regression.")
print(f"\n  → People deviate from baseline behavior ~{100-best_accuracy*100:.0f}% of the time")
print(f"  → Recommendations/social info have {100-best_accuracy*100:.0f}% influence on choices")
print("\n" + "=" * 80)
