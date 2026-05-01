import pandas as pd

from finstream.interfaces.i_transformer import ITransformer


class Deduplicator(ITransformer):
    """Remove duplicate transaction ids within a chunk, keeping first occurrence."""

    def transformer_name(self) -> str:
        return "Deduplicator"

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop rows whose id already appeared earlier in the chunk.

        Args:
            df: DataFrame chunk to deduplicate.

        Returns:
            DataFrame with unique transaction ids, preserving row order.
        """
        return df.drop_duplicates(subset=["id"], keep="first").reset_index(drop=True)
