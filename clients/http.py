from __future__ import annotations

import time
from typing import Any

import requests

from clients.exceptions import ExternalResponseError, ServiceUnavailableError

DEFAULT_TIMEOUT_SECONDS = 8
MAX_ATTEMPTS = 3
TRANSIENT_STATUS_CODES = {500, 502, 503, 504}


class HttpClient:
    """Small GET-only HTTP client with retries for temporary failures."""

    def __init__(self, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> None:
        self.timeout = timeout
        self.session = requests.Session()

    def get_json(
        self, url: str, *, params: dict[str, str | int | float] | None = None
    ) -> dict[str, Any] | list[Any]:
        last_error: Exception | None = None

        for attempt in range(MAX_ATTEMPTS):
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
            except (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
            ) as error:
                last_error = error
                if attempt < MAX_ATTEMPTS - 1:
                    time.sleep(1)
                    continue
                raise ServiceUnavailableError(
                    "Не удалось подключиться к внешнему сервису."
                ) from error

            if response.status_code == 429:
                last_error = ServiceUnavailableError(
                    "Внешний сервис временно ограничил запросы."
                )
                if attempt < MAX_ATTEMPTS - 1:
                    time.sleep(
                        _retry_after_seconds(response.headers.get("Retry-After"))
                    )
                    continue
                raise last_error

            if response.status_code in TRANSIENT_STATUS_CODES:
                last_error = ServiceUnavailableError(
                    f"Внешний сервис временно недоступен (HTTP {response.status_code})."
                )
                if attempt < MAX_ATTEMPTS - 1:
                    time.sleep(1)
                    continue
                raise last_error

            if not 200 <= response.status_code < 300:
                raise ExternalResponseError(
                    f"Внешний сервис вернул HTTP {response.status_code}."
                )

            try:
                payload = response.json()
            except ValueError as error:
                raise ExternalResponseError("Внешний сервис вернул не JSON.") from error

            if not isinstance(payload, (dict, list)):
                raise ExternalResponseError(
                    "JSON-ответ внешнего сервиса имеет неверный формат."
                )
            return payload

        raise ServiceUnavailableError("Внешний сервис недоступен.") from last_error


def _retry_after_seconds(header_value: str | None) -> int:
    """Return numeric Retry-After safely; use one second for missing/invalid values."""
    if header_value is None:
        return 1
    try:
        seconds = int(header_value)
    except ValueError:
        return 1
    return max(seconds, 0)
