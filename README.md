# marimo vs Jupyter: CI Comparison

This repository demonstrates the difference in CI/CD experience between
[marimo](https://marimo.io/) notebooks (`.py`) and Jupyter notebooks (`.ipynb`).

Both notebooks perform the same synthetic sales data analysis. The difference
is in how standard CI tools interact with each format.

## Comparison

| CI Step | marimo (`.py`) | Jupyter (`.ipynb`) |
|---------|---------------|-------------------|
| Lint | `uv run ruff check` | `uv run nbqa ruff` (wrapper needed) |
| Test | `uv run pytest` | `uv run pytest --nbmake` (plugin needed) |
| Execute | `uv run python notebook.py` | `uv run jupyter nbconvert --execute` (tool needed) |
| Git diff | Clean, readable Python | JSON noise |

## Directory structure

```
notebooks/
├── marimo/
│   ├── analysis.py          # Plain Python — ruff, pytest, python all work directly
│   └── test_analysis.py     # pytest discovers test_ cells automatically
└── jupyter/
    ├── analysis.ipynb        # Needs nbqa, nbmake, nbconvert wrappers
    └── test_analysis.ipynb   # Needs nbmake plugin for pytest
src/
└── helpers.py                # Shared helper functions imported by both notebooks
tests/
└── test_helpers.py           # Standard unit tests for helpers
```

## Run locally

```bash
# Install dependencies
uv sync

# --- marimo (standard tools, no wrappers) ---
uv run ruff check notebooks/marimo/
uv run pytest notebooks/marimo/test_analysis.py -v
uv run python notebooks/marimo/analysis.py

# --- Jupyter (every step needs a wrapper) ---
uv run nbqa ruff notebooks/jupyter/
uv run pytest --nbmake notebooks/jupyter/test_analysis.ipynb -v
uv run jupyter nbconvert --to notebook --execute notebooks/jupyter/analysis.ipynb
```

## GitHub Actions

- [CI (marimo)](.github/workflows/ci-marimo.yml) — ruff + pytest + python, no extra tools
- [CI (Jupyter)](.github/workflows/ci-jupyter.yml) — nbqa + nbmake + nbconvert wrappers

## Key takeaway

marimo notebooks are plain `.py` files. Every tool in the Python ecosystem works
on them without adapters. Jupyter's `.ipynb` format requires a wrapper for each
CI step.
