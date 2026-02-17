"""Shared helper functions for sales data analysis."""


def calculate_growth_rate(current: float, previous: float) -> float | None:
    """Calculate percentage growth rate between two values.

    Args:
        current: The current period value.
        previous: The previous period value.

    Returns:
        Growth rate as a percentage, or None if previous is zero.
    """
    if previous == 0:
        return None
    return ((current - previous) / previous) * 10
