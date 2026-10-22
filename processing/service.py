from typing import Any

from clients.rates import get_rate
from clients.weather import get_weather
from processing.preprocessing import enrich_rate, enrich_weather


def build_city_summary(city: str, currency: str = "USD") -> dict[str, Any]:
    """Build a normalized weather and exchange-rate summary for a city."""
    weather = get_weather(city)
    rate = get_rate(currency)
    return {
        "city": city,
        "weather": enrich_weather(weather),
        "rates": enrich_rate(currency, rate),
    }
