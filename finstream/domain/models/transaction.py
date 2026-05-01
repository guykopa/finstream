from dataclasses import dataclass
from datetime import date

from finstream.domain.models.currency import Currency


@dataclass(frozen=True)
class Transaction:
    """Represents a single financial transaction.

    Attributes:
        id: Unique transaction identifier.
        amount: Transaction amount in the original currency.
        currency: ISO currency code.
        entity: Business entity or counterpart identifier.
        date: Business date of the transaction.
        source: Origin system (postgresql, csv, api).
    """

    id: str
    amount: float
    currency: Currency
    entity: str
    date: date
    source: str
