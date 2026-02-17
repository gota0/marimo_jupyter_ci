import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import random

    from src.helpers import calculate_growth_rate

    return (calculate_growth_rate, random)


@app.cell
def _(random):
    random.seed(42)
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    sales = [random.randint(80, 200) for _ in months]
    return (months, sales)


@app.cell
def _(calculate_growth_rate, months, sales):
    growth_rates = []
    for i in range(1, len(sales)):
        rate = calculate_growth_rate(sales[i], sales[i - 1])
        growth_rates.append((months[i], rate))
    return (growth_rates,)


@app.cell
def _(growth_rates, mo, months, sales):
    best_month, best_rate = max(
        growth_rates,
        key=lambda pair: pair[1] if pair[1] is not None else float("-inf"),
    )

    rows = "\n".join(f"| {months[i]} | {sales[i]} |" for i in range(len(months)))

    mo.md(
        f"""# Monthly Sales Analysis

| Month | Sales |
|-------|-------|
{rows}

**Highest growth:** {best_month} ({best_rate:.1f}%)"""
    )
    return


if __name__ == "__main__":
    app.run()
