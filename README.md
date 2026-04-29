# BobaLab Analysis

This repository contains the scripts and outputs for the BobaLab food truck case study.

## Layout

- `data/` contains the input CSV files used by the analysis scripts.
- `results/` contains generated figures and other derived outputs.
- The Python scripts in the repository root reproduce the printed analysis and charts.

## Run the analysis

1. Activate the virtual environment.
2. Run:

```powershell
python main.py
```

The script reads from `data/` and writes figures to `results/`.

## Notes

- Generated PNG files in `results/` are ignored by Git.
- Keep new input data in `data/` so the analysis scripts can find it without path changes.
