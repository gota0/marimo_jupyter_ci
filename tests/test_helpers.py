"""Standard pytest tests for src.helpers."""

import pytest

from src.helpers import calculate_growth_rate


def test_positive_growth():
    assert calculate_growth_rate(110, 100) == pytest.approx(10.0)


def test_negative_growth():
    assert calculate_growth_rate(90, 100) == pytest.approx(-10.0)


def test_zero_previous_returns_none():
    assert calculate_growth_rate(100, 0) is None


def test_no_change():
    assert calculate_growth_rate(100, 100) == pytest.approx(0.0)


def test_large_growth():
    assert calculate_growth_rate(300, 100) == pytest.approx(200.0)


def test_decline_to_zero():
    assert calculate_growth_rate(0, 100) == pytest.approx(-100.0)
