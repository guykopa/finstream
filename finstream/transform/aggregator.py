import pandas as pd

from finstream.interfaces.i_transformer import ITransformer


class Aggregator(ITransformer):
    """Group transactions by entity and sum their amounts."""

    def transformer_name(self) -> str:
        return "Aggregator"

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate amounts by entity, collapsing to one row per entity.

        Args:
            df: DataFrame chunk with 'entity' and 'amount' columns.

        Returns:
            DataFrame with one row per entity and the summed amount.
        """
        if df.empty or "entity" not in df.columns:
            return df.copy()

        return (
            df.groupby("entity", as_index=False)["amount"]
            .sum()
            .reset_index(drop=True)
        )
