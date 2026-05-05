"""Common filesystem paths used across analysis scripts."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"


def data_file(filename: str) -> Path:
    """Return an absolute path inside the data directory."""
    return DATA_DIR / filename


def ensure_results_dir() -> Path:
    """Create the results directory if needed and return it."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    return RESULTS_DIR