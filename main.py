from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from typing import Any

from clients.exceptions import (
    CityNotFoundError,
    CurrencyNotFoundError,
    ExternalServiceError,
    ServiceUnavailableError,
)
from processing.service import build_city_summary

CURRENCY_PATTERN = re.compile(r"^[A-Za-z]{3}$")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Печатает погоду и курс валюты к рублю."
    )
    parser.add_argument(
        "--city", required=True, help="Название города, например Moscow"
    )
    parser.add_argument(
        "--currency",
        default="USD",
        help="Трёхбуквенный ISO-код валюты (по умолчанию USD)",
    )
    args = parser.parse_args(argv)
    if not args.city.strip():
        parser.error("--city не может быть пустым")
    if not CURRENCY_PATTERN.fullmatch(args.currency):
        parser.error("--currency должен содержать трёхбуквенный ISO-код")
    args.city = args.city.strip()
    args.currency = args.currency.upper()
    return args


def format_summary(summary: dict[str, Any]) -> str:
    weather = summary["weather"]
    rates = summary["rates"]
    warm_clothes = "да" if weather["warm_clothes"] else "нет"
    expensive = "да" if rates["expensive"] else "нет"
    return "\n".join(
        (
            f"Город: {summary['city']}",
            f"Погода: {weather['temp_c']:.1f}°C, {weather['description']}",
            f"Тёплая одежда: {warm_clothes}",
            f"{rates['currency']}→RUB: {rates['rate_to_rub']:.2f}",
            f"Дорогой курс: {expensive}",
        )
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = build_city_summary(args.city, args.currency)
    except (CityNotFoundError, CurrencyNotFoundError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 3
    except (ServiceUnavailableError, ExternalServiceError) as error:
        print(f"Ошибка внешнего сервиса: {error}", file=sys.stderr)
        return 4

    print(format_summary(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
