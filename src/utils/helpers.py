"""Shared formatting and validation utilities."""

from datetime import date


def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    """Clamp value to [lo, hi]."""
    return max(lo, min(hi, value))


def years_since(founding_year: int) -> int:
    """Return number of complete years since founding_year."""
    return date.today().year - founding_year


def format_currency(amount: float, symbol: str = "€") -> str:
    """Format a float as a human-readable currency string."""
    return f"{symbol}{amount:,.0f}"


def score_to_color(score: float) -> str:
    """Map a 0–100 score to a hex colour for UI display."""
    if score >= 70:
        return "#2ECC71"   # green
    if score >= 50:
        return "#F39C12"   # amber
    return "#E74C3C"       # red
