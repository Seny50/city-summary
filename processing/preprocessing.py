from typing import Any


def enrich_weather(weather: dict[str, Any]) -> dict[str, Any]:
    """Add presentation-ready weather rules to normalized weather data."""
    result = dict(weather)
    result["warm_clothes"] = result["temp_c"] < 0
    if not str(result.get("description", "")).strip():
        result["description"] = "описание недоступно"
    return result


def enrich_rate(currency: str, rate_to_rub: float) -> dict[str, Any]:
    """Add rate-related rules to a normalized currency rate."""
    return {
        "currency": currency.upper(),
        "rate_to_rub": rate_to_rub,
        "expensive": rate_to_rub > 100,
    }
