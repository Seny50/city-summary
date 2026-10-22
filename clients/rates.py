from __future__ import annotations

import time
from typing import Any

from clients.exceptions import (
    CurrencyNotFoundError,
    ExternalResponseError,
)
from clients.http import HttpClient

FRANKFURTER_RATE_URL = "https://api.frankfurter.dev/v2/rate/{currency}/RUB"
CACHE_TTL_SECONDS = 300
_rate_cache: dict[str, tuple[float, float]] = {}


def get_rate(currency: str, http_client: HttpClient | None = None) -> float:
    """Fetch a currency-to-ruble rate and keep it in memory for five minutes."""
    normalized_currency = currency.upper()
    cached = _rate_cache.get(normalized_currency)
    now = time.monotonic()
    if cached is not None and now - cached[0] < CACHE_TTL_SECONDS:
        return cached[1]

    client = http_client or HttpClient()
    try:
        payload = client.get_json(
            FRANKFURTER_RATE_URL.format(currency=normalized_currency)
        )
    except ExternalResponseError as error:
        raise CurrencyNotFoundError("Код валюты не найден.") from error
    rate = _rate_from_payload(payload)
    _rate_cache[normalized_currency] = (now, rate)
    return rate


def _rate_from_payload(payload: dict[str, Any] | list[Any]) -> float:
    if isinstance(payload, dict) and payload.get("error"):
        raise CurrencyNotFoundError("Код валюты не найден.")
    if not isinstance(payload, dict):
        raise ExternalResponseError("Сервис курсов вернул ответ неверного формата.")
    rate = payload.get("rate")
    if not isinstance(rate, (int, float)) or isinstance(rate, bool):
        raise CurrencyNotFoundError("Код валюты не найден или в ответе нет курса.")
    return float(rate)
