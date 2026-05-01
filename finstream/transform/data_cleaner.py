"""Transformer that removes malformed rows before business transformations."""
import pandas as pd

from finstream.interfaces.i_transformer import ITransformer

_VALID_CURRENCIES = {"EUR", "USD", "GBP", "CHF"}


class DataCleaner(ITransformer):
    """Drop rows with invalid amounts or unknown currencies.

    Rows are removed rather than corrected — callers can inspect
    the returned DataFrame's length vs the input to count rejections.
    """

    def transformer_name(self) -> str:
        return "DataCleaner"

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove rows with non-positive amounts or unsupported currencies.

        Args:
            df: Raw DataFrame chunk.

        Returns:
            DataFrame with only clean, processable rows.
        """
        result = df.copy()
        result = result[result["amount"].notna() & (result["amount"] > 0)]
        has_null_currency = result["currency"].isna()
        has_invalid_currency = ~result["currency"].isin(_VALID_CURRENCIES)
        result = result[has_null_currency | ~has_invalid_currency]
        return result.reset_index(drop=True)
