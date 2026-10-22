import io
import json
import unittest
from unittest.mock import patch

import main


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
