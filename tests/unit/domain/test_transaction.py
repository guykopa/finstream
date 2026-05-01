import dataclasses
from datetime import date

import pytest

from finstream.domain.models.currency import Currency
from finstream.domain.models.transaction import Transaction


def _make_tx(**kwargs) -> Transaction:
    defaults = dict(
        id="tx-001",
        amount=100.0,
        currency=Currency.EUR,
        entity="Apple",
        date=date(2024, 1, 15),
        source="csv",
    )
    defaults.update(kwargs)
    return Transaction(**defaults)


class TestTransaction:
    def test_fields_are_accessible(self) -> None:
        tx = _make_tx()
        assert tx.id == "tx-001"
        assert tx.amount == 100.0
        assert tx.currency == Currency.EUR
        assert tx.entity == "Apple"
        assert tx.date == date(2024, 1, 15)
        assert tx.source == "csv"

    def test_is_immutable(self) -> None:
        tx = _make_tx()
        with pytest.raises(dataclasses.FrozenInstanceError):
            tx.amount = 999.0  # type: ignore[misc]

    def test_equal_when_all_fields_match(self) -> None:
        assert _make_tx() == _make_tx()

    def test_not_equal_when_id_differs(self) -> None:
        assert _make_tx(id="tx-001") != _make_tx(id="tx-002")

    def test_not_equal_when_amount_differs(self) -> None:
        assert _make_tx(amount=100.0) != _make_tx(amount=200.0)

    def test_all_currencies_accepted(self) -> None:
        for currency in Currency:
            tx = _make_tx(currency=currency)
            assert tx.currency == currency
