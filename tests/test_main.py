import io
import json
import unittest
from unittest.mock import patch

import main
from clients.exceptions import CurrencyNotFoundError


class MainTests(unittest.TestCase):
    @patch("main.build_city_summary")
    def test_json_output(self, build_summary: object) -> None:
        build_summary.return_value = {
            "city": "Moscow",
            "weather": {"temp_c": -3.2, "description": "ясно", "warm_clothes": True},
            "rates": {"currency": "USD", "rate_to_rub": 92.15, "expensive": False},
        }
        stdout = io.StringIO()

        with patch("sys.stdout", stdout):
            exit_code = main.main(["--city", "Moscow", "--json"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["city"], "Moscow")

    @patch("main.build_city_summary")
    def test_missing_currency_returns_exit_code_three(
        self, build_summary: object
    ) -> None:
        build_summary.side_effect = CurrencyNotFoundError("Код валюты не найден.")
        stderr = io.StringIO()

        with patch("sys.stderr", stderr):
            exit_code = main.main(["--city", "Moscow", "--currency", "ZZZ"])

        self.assertEqual(exit_code, 3)
        self.assertIn("Код валюты не найден", stderr.getvalue())

    @patch("main.build_city_summary")
    def test_currency_defaults_to_usd(self, build_summary: object) -> None:
        build_summary.return_value = {
            "city": "Moscow",
            "weather": {"temp_c": 1.0, "description": "ясно", "warm_clothes": False},
            "rates": {"currency": "USD", "rate_to_rub": 90.0, "expensive": False},
        }
        stdout = io.StringIO()

        with patch("sys.stdout", stdout):
            exit_code = main.main(["--city", "Moscow"])

        self.assertEqual(exit_code, 0)
        build_summary.assert_called_once_with("Moscow", "USD")
