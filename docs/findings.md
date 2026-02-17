# Findings: marimo vs Jupyter CI Comparison

This document explains what this repository demonstrates and what I learned from building it.

## Why this repo exists

I recently discovered [marimo](https://marimo.io/) and got curious about what its `.py` file format means for CI. Not every notebook needs CI — but some notebooks get reused, shared across a team, or become the basis for a recurring report. For those, it'd be nice to know they actually run on a clean machine.

Setting up CI for Jupyter's `.ipynb` files can be annoying. There are lots of Jupyter notebooks on GitHub, but almost none have CI. I wanted to see if marimo's `.py` format made CI easier, so I built this repo to compare them side by side.

## The comparison

Both notebooks do the same synthetic sales analysis. Both CI pipelines use [uv](https://docs.astral.sh/uv/) for dependency management, [ruff](https://docs.astral.sh/ruff/) for linting, and [pytest](https://docs.pytest.org/) for testing.

| CI Step | marimo (`.py`) | Jupyter (`.ipynb`) |
|---------|---------------|-------------------|
| **Lint** | `uv run ruff check` | `uv run nbqa ruff` |
| **Type-check** | `uv run pyright` | No clean option |
| **Test** | `uv run pytest` | `uv run pytest --nbmake` |
| **Execute** | `uv run python notebook.py` | `uv run jupyter nbconvert --execute` |
| **Git diff** | Clean Python | JSON wall |

Every marimo step uses tools you already know. Every Jupyter step needs a wrapper — and for type-checking, there's no clean option at all.

The GitHub Actions workflows are at [`.github/workflows/ci-marimo.yml`](../.github/workflows/ci-marimo.yml) and [`.github/workflows/ci-jupyter.yml`](../.github/workflows/ci-jupyter.yml). The marimo workflow:

```yaml
- run: uv run ruff check notebooks/marimo/
- run: uv run pyright notebooks/marimo/ src/
- run: uv run pytest notebooks/marimo/ -v
- run: uv run python notebooks/marimo/analysis.py
```

The Jupyter workflow:

```yaml
- run: uv run nbqa ruff notebooks/jupyter/
# pyright? No clean equivalent for .ipynb
- run: uv run pytest --nbmake notebooks/jupyter/ -v
- run: uv run jupyter nbconvert --to notebook --execute notebooks/jupyter/analysis.ipynb
```

Same steps. The marimo version uses ruff, pyright, pytest, and python directly. The Jupyter version wraps what it can and skips what it can't.

## Finding 1: Git diff noise

I didn't change a single line of code. I just opened the Jupyter notebook in my browser, ran it, and committed. Here's what `git diff` looked like:

```diff
-   "execution_count": null,
+   "execution_count": 1,
    "id": "1f1c05a2",
    "metadata": {},
...
-   "execution_count": null,
+   "execution_count": 3,
    "id": "9c42f8c1",
    "metadata": {},
-   "outputs": [],
+   "outputs": [
+    {
+     "name": "stdout",
+     "output_type": "stream",
+     "text": [
+      "Jan: 161\n",
+      "Feb: 94\n",
+      "Mar: 83\n",
+      ...
+     ]
+    }
+   ],
...
+  "language_info": {
+   "codemirror_mode": {
+    "name": "ipython",
+    "version": 3
+   },
+   "file_extension": ".py",
+   "mimetype": "text/x-python",
+   "name": "python",
+   "pygments_lexer": "ipython3",
+   "version": "3.12.12"
   }
```

90+ lines of diff noise from zero code changes. Execution counts, embedded stdout, kernel metadata, language info — all baked into the file format.

The marimo notebook? I ran it too. `git diff` showed nothing, because there's nothing to track. The `.py` file is just your code.

## Finding 2: The import workaround chain

Both notebooks import a shared helper from [`src/helpers.py`](../src/helpers.py). In the marimo notebook ([`notebooks/marimo/analysis.py`](../notebooks/marimo/analysis.py)), it's a normal import:

```python
@app.cell
def _():
    from src.helpers import calculate_growth_rate
    return (calculate_growth_rate,)
```

`pythonpath = ["."]` in `pyproject.toml` handles resolution, and since the import lives inside an `@app.cell` function, ruff treats it as regular code. No issues.

In the Jupyter notebook ([`notebooks/jupyter/analysis.ipynb`](../notebooks/jupyter/analysis.ipynb)), the same import needs a `sys.path` hack because the notebook lives in `notebooks/jupyter/` and can't find `src/` without help:

```python
import sys
sys.path.insert(0, "../..")
from src.helpers import calculate_growth_rate  # noqa: E402
```

That `# noqa: E402` was unavoidable. ruff's E402 rule flags module-level imports that aren't at the top of the file, and `from src.helpers import ...` *has* to come after `sys.path.insert()`. The import can't move above the path manipulation that makes it work.

This is a pattern I kept running into: with `.ipynb`, every workaround you add to fix one thing (path manipulation) creates a new problem (lint violation) that needs its own workaround (`# noqa`). With `.py` files, the toolchain just works and you don't end up in these chains.

## Finding 3: Type-checking has no workaround

For linting and testing, Jupyter at least has wrappers — nbqa for ruff, nbmake for pytest. They're extra dependencies, but they work. Type-checking is where the gap gets wider: there's no clean way to run pyright on `.ipynb` files.

For marimo, it just works:

```bash
uv run pyright notebooks/marimo/ src/
```

pyright reads the `.py` files, checks the types, done. We added type hints to [`src/helpers.py`](../src/helpers.py) and pyright catches any mismatches in both the helper module and the notebook code that calls it.

For Jupyter, you could try `uv run nbqa pyright notebooks/jupyter/`, but nbqa + pyright has known limitations with notebook cell scoping. In our CI workflow ([`ci-jupyter.yml`](../.github/workflows/ci-jupyter.yml)), we run it as a best-effort step that logs a warning rather than failing the build — because it doesn't work reliably enough to gate on.

The other tools at least have a "wrapper needed" story. Type-checking has a "no clean option" story.

## Finding 4: Test granularity

marimo supports pytest natively. Name a cell `test_` and pytest discovers it as an individual test. See [`notebooks/marimo/test_analysis.py`](../notebooks/marimo/test_analysis.py) for the full file.

I deliberately broke `calculate_growth_rate` to see what failure looks like in both formats. Here's what pytest reports for the marimo CI run:

```
notebooks/marimo/test_analysis.py::test_positive_growth FAILED           [ 10%]
notebooks/marimo/test_analysis.py::test_negative_growth FAILED           [ 20%]
notebooks/marimo/test_analysis.py::test_zero_previous_returns_none PASSED [ 30%]
notebooks/marimo/test_analysis.py::test_no_change PASSED                 [ 40%]
tests/test_helpers.py::test_positive_growth FAILED                       [ 50%]
tests/test_helpers.py::test_negative_growth FAILED                       [ 60%]
tests/test_helpers.py::test_zero_previous_returns_none PASSED            [ 70%]
tests/test_helpers.py::test_no_change PASSED                             [ 80%]
tests/test_helpers.py::test_large_growth FAILED                          [ 90%]
tests/test_helpers.py::test_decline_to_zero FAILED                       [100%]

6 failed, 4 passed in 0.90s
```

Ten individual tests across the notebook and unit tests. Six failed, four passed. You know exactly which functions broke — both in the marimo notebook cells and in the standard test file. pytest treats them identically.

Here's the same CI run for Jupyter:

```
notebooks/jupyter/analysis.ipynb::analysis.ipynb PASSED                  [ 12%]
notebooks/jupyter/test_analysis.ipynb::test_analysis.ipynb FAILED        [ 25%]
tests/test_helpers.py::test_positive_growth FAILED                       [ 37%]
tests/test_helpers.py::test_negative_growth FAILED                       [ 50%]
tests/test_helpers.py::test_zero_previous_returns_none PASSED            [ 62%]
tests/test_helpers.py::test_no_change PASSED                             [ 75%]
tests/test_helpers.py::test_large_growth FAILED                          [ 87%]
tests/test_helpers.py::test_decline_to_zero FAILED                       [100%]

5 failed, 3 passed in 3.19s
```

The `tests/test_helpers.py` results are identical — those are standard `.py` tests, so pytest handles them the same way. The difference is in the notebook lines: marimo produced four individual test results (`test_positive_growth`, `test_negative_growth`, `test_zero_previous_returns_none`, `test_no_change`), while nbmake collapsed the entire Jupyter test notebook into one line (`test_analysis.ipynb FAILED`). It hit the first failing assertion and stopped — you never find out whether the other test cells would have passed.

The error messages are fine in both cases — you can see expected vs actual values either way. The difference is granularity: marimo gives you per-function results from the notebook itself, while nbmake treats the whole notebook as one pass/fail.

## Conclusion

This isn't a "Jupyter is bad" repo. Jupyter's ecosystem is massive, `.ipynb` renders nicely on GitHub, and it supports tons of languages. For quick exploration where you want outputs saved inline, it's great.

But if you have notebooks that get shared around or reused — the kind where you want to make sure they actually run — the file format makes a real difference. `.py` files slot into whatever Python CI setup you already have. `.ipynb` files need a parallel toolchain, and in practice that means most people skip CI entirely.

## Reproducing

```bash
uv sync

# marimo (standard tools, no wrappers)
uv run ruff check notebooks/marimo/
uv run pyright notebooks/marimo/ src/
uv run pytest notebooks/marimo/test_analysis.py -v
uv run python notebooks/marimo/analysis.py

# Jupyter (every step needs a wrapper)
uv run nbqa ruff notebooks/jupyter/
# uv run nbqa pyright notebooks/jupyter/  # best-effort, has limitations
uv run pytest --nbmake notebooks/jupyter/test_analysis.ipynb -v
uv run jupyter nbconvert --to notebook --execute notebooks/jupyter/analysis.ipynb
```