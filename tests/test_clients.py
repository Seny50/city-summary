import unittest
from unittest.mock import Mock, patch

import requests

from clients.exceptions import CityNotFoundError, ServiceUnavailableError
from clients.http import HttpClient
from clients.rates import _rate_cache, get_rate
from clients.weather import get_weather


class WeatherClientTests(unittest.TestCase):
    def test_get_weather_normalizes_open_meteo_responses(self) -> None:
        client = Mock()
        client.get_json.side_effect = [
            {"results": [{"latitude": 55.75, "longitude": 37.62}]},
            {"current": {"temperature_2m": -3.2, "weather_code": 0}},
        ]

        weather = get_weather("Moscow", client)

        self.assertEqual(weather, {"temp_c": -3.2, "description": "ясно"})
        self.assertEqual(client.get_json.call_count, 2)

    def test_get_weather_raises_for_missing_city(self) -> None:
        client = Mock()
        client.get_json.return_value = {"results": []}

        with self.assertRaises(CityNotFoundError):
            get_weather("No such city", client)


class RateClientTests(unittest.TestCase):
    def setUp(self) -> None:
        _rate_cache.clear()

    def test_get_rate_normalizes_frankfurter_response(self) -> None:
        client = Mock()
        client.get_json.return_value = {"rate": 92.15}

        rate = get_rate("usd", client)

        self.assertEqual(rate, 92.15)
        client.get_json.assert_called_once()


class HttpClientTests(unittest.TestCase):
    @patch("clients.http.time.sleep")
    def test_retries_temporary_server_error_three_times(self, sleep: Mock) -> None:
        response = Mock(status_code=503, headers={})
        session = Mock()
        session.get.return_value = response
        client = HttpClient()
        client.session = session

        with self.assertRaises(ServiceUnavailableError):
            client.get_json("https://example.test")

        self.assertEqual(session.get.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    @patch("clients.http.time.sleep")
    def test_retries_connection_error_three_times(self, sleep: Mock) -> None:
        session = Mock()
        session.get.side_effect = requests.exceptions.ConnectionError("offline")
        client = HttpClient()
        client.session = session

        with self.assertRaises(ServiceUnavailableError):
            client.get_json("https://example.test")

        self.assertEqual(session.get.call_count, 3)
        self.assertEqual(sleep.call_count, 2)
