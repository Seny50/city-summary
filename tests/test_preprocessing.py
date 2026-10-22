import unittest

from processing.preprocessing import enrich_rate, enrich_weather


class PreprocessingTests(unittest.TestCase):
    def test_weather_marks_warm_clothes_below_zero(self) -> None:
        weather = enrich_weather({"temp_c": -3.2, "description": "ясно"})

        self.assertTrue(weather["warm_clothes"])

    def test_weather_keeps_warm_clothes_false_at_zero(self) -> None:
        weather = enrich_weather({"temp_c": 0.0, "description": ""})

        self.assertFalse(weather["warm_clothes"])
        self.assertEqual(weather["description"], "описание недоступно")

    def test_rate_marks_expensive_above_hundred_rubles(self) -> None:
        rate = enrich_rate("eur", 101.5)

        self.assertEqual(rate["currency"], "EUR")
        self.assertTrue(rate["expensive"])
