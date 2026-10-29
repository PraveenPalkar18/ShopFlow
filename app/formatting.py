from decimal import Decimal, ROUND_DOWN


def format_money(value: float | Decimal) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_DOWN))
