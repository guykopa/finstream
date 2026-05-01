import pandas as pd

from finstream.domain.exceptions import TransformationError
from finstream.interfaces.i_transformer import ITransformer


class CurrencyNormalizer(ITransformer):
    """Convert all transaction amounts to EUR using injected exchange rates.

    Rates are provided at construction time so the transformer stays stateless
    and fully testable without any network call.
    """

    def __init__(self, rates: dict[str, float]) -> None:
        self._rates = rates

    def transformer_name(self) -> str:
        return "CurrencyNormalizer"

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Multiply each amount by its EUR conversion rate.

        Args:
            df: DataFrame chunk with 'amount' and 'currency' columns.

        Returns:
            DataFrame with amounts converted to EUR and currency set to 'EUR'.

        Raises:
            TransformationError: if a currency has no configured rate.
        """
        # Null and unknown currencies are left unchanged — quality rules will catch them.
        result = df.copy()
        has_rate = result["currency"].isin(self._rates)
        original_dtype = result["amount"].dtype
        converted = result.loc[has_rate].apply(
            lambda row: row["amount"] * self._rates[row["currency"]], axis=1
        ).astype(original_dtype)
        result.loc[has_rate, "amount"] = converted
        result.loc[has_rate, "currency"] = "EUR"
        return result
