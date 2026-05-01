from enum import Enum


class Currency(str, Enum):
    """Supported transaction currencies."""

    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    CHF = "CHF"
