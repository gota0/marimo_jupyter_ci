import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _():
    import pytest

    from src.helpers import calculate_growth_rate

    return (calculate_growth_rate, pytest)


@app.cell
def test_positive_growth(calculate_growth_rate, pytest):
    assert calculate_growth_rate(110, 100) == pytest.approx(10.0)


@app.cell
def test_negative_growth(calculate_growth_rate, pytest):
    assert calculate_growth_rate(90, 100) == pytest.approx(-10.0)


@app.cell
def test_zero_previous_returns_none(calculate_growth_rate):
    assert calculate_growth_rate(100, 0) is None


@app.cell
def test_no_change(calculate_growth_rate, pytest):
    assert calculate_growth_rate(100, 100) == pytest.approx(0.0)


if __name__ == "__main__":
    app.run()
