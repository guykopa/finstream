import pandas as pd

from finstream.interfaces.i_transformer import ITransformer


class DateStandardizer(ITransformer):
    """Normalize the date column to timezone-naive datetime64[ns] UTC."""

    def transformer_name(self) -> str:
        return "DateStandardizer"

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse and standardize the date column to naive UTC datetimes.

        Args:
            df: DataFrame chunk with a 'date' column in any parseable format.

        Returns:
            DataFrame with 'date' as timezone-naive datetime64[ns].
        """
        if df.empty or "date" not in df.columns:
            return df.copy()

        result = df.copy()
        dates = pd.to_datetime(result["date"], utc=True)
        result["date"] = dates.dt.tz_localize(None)
        return result
