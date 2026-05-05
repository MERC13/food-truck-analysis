# BobaLab Analysis Workspace

This repository contains analysis scripts for the BobaLab food truck study.
The code is organized for reproducible reruns with data in `data/` and generated artifacts in `results/`.

## Quick Start

1. Create and activate a Python environment.
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the main analysis:

```powershell
python main.py
```

## Repository Layout

- `data/`: source CSV files used by all analyses.
- `results/`: generated figures and JSON outputs.
- `project_paths.py`: shared path helper used by scripts.

## Script Guide

- `main.py`
	- End-to-end descriptive analysis and CI-based plots.
	- Generates multiple PNGs in `results/`.
- `baseline_model.py`
	- Day 2 baseline policy model evaluated on days 3-8.
	- Saves `baseline_model_predictions.png` and `baseline_model_results.json`.
- `baseline_model_improved.py`
	- Compares several baseline-prediction approaches.
	- Saves `baseline_model_improved.png`.
- `strategy_cluster_analysis.py`
	- Participant strategy clustering with silhouette-based model selection.
- `efficient_microcluster_analysis.py`
	- Sub-clustering within the efficient participant subgroup.
- `recommendation_design_analysis.py`
	- Prints recommendation-system design principles based on observed behavior.
- `check_conditions.py`
	- Quick integrity check of day-level experiment condition columns.
- `optimize_recommendation_policy.py`
	- Fast policy analysis for fixed advice frequency, day-by-day schedules, and a state-plus-history advice rule.
	- Prints the preferred policy in minutes rather than hours.

## Figures and Outputs

- `results/microcluster_profiles_3_ci.png` uses the named efficient-player clusters:
  - High-Earner Deliberators
  - Independent Progressives
  - Advice-Purists

## Reproducibility Notes

- All scripts resolve paths relative to the repository root via `project_paths.py`.
- Scripts create `results/` automatically when needed.
- Generated PNG files are ignored by Git; keep derived outputs in `results/`.

## Typical Workflow for Researchers

1. Validate input tables with `python check_conditions.py`.
2. Run `python main.py` for primary analysis outputs.
3. Run targeted scripts (`baseline_model.py`, clustering scripts) for follow-up questions.
4. Keep narrative conclusions in markdown files, and keep raw generated files in `results/`.
