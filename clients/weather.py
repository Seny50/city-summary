from typing import Any

from clients.exceptions import CityNotFoundError, ExternalResponseError
from clients.http import HttpClient

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_DESCRIPTIONS = {
    0: "ясно",
    1: "преимущественно ясно",
    2: "переменная облачность",
    3: "пасмурно",
    45: "туман",
    48: "изморозь",
    51: "слабая морось",
    53: "морось",
    55: "сильная морось",
    61: "небольшой дождь",
    63: "дождь",
    65: "сильный дождь",
    71: "небольшой снег",
    73: "снег",
    75: "сильный снег",
    80: "ливень",
    81: "ливень",
    82: "сильный ливень",
    95: "гроза",
}


def get_weather(
    city: str, http_client: HttpClient | None = None
) -> dict[str, float | str]:
    """Fetch current temperature and weather description for a city."""
    client = http_client or HttpClient()
    geocoding = client.get_json(
        GEOCODING_URL,
        params={"name": city, "count": 1, "language": "ru", "format": "json"},
    )
    latitude, longitude = _coordinates_from_geocoding(geocoding)
    forecast = client.get_json(
        FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,weather_code",
        },
    )
    return _weather_from_forecast(forecast)


def _coordinates_from_geocoding(
    payload: dict[str, Any] | list[Any],
) -> tuple[float, float]:
    if not isinstance(payload, dict):
        raise ExternalResponseError("Геокодер вернул ответ неверного формата.")
    results = payload.get("results")
    if not isinstance(results, list) or not results:
        raise CityNotFoundError("Город не найден.")
    first_result = results[0]
    if not isinstance(first_result, dict):
        raise ExternalResponseError("Геокодер вернул некорректные данные города.")
    latitude = first_result.get("latitude")
    longitude = first_result.get("longitude")
    if not _is_number(latitude) or not _is_number(longitude):
        raise ExternalResponseError("В ответе геокодера нет координат города.")
    return float(latitude), float(longitude)


def _weather_from_forecast(
    payload: dict[str, Any] | list[Any],
) -> dict[str, float | str]:
    if not isinstance(payload, dict):
        raise ExternalResponseError("Сервис погоды вернул ответ неверного формата.")
    current = payload.get("current")
    if not isinstance(current, dict):
        raise ExternalResponseError("В ответе погоды отсутствует блок current.")
    temperature = current.get("temperature_2m")
    weather_code = current.get("weather_code")
    if not _is_number(temperature) or not isinstance(weather_code, int):
        raise ExternalResponseError("В ответе погоды отсутствуют обязательные поля.")
    return {
        "temp_c": float(temperature),
        "description": WEATHER_DESCRIPTIONS.get(
            weather_code, "неизвестные погодные условия"
        ),
    }


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)
