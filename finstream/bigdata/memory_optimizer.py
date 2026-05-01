import pandas as pd

# Object columns with fewer unique values than this ratio are categorized.
_CATEGORY_THRESHOLD = 0.5


class MemoryOptimizer:
    """Reduce DataFrame memory footprint by downcasting dtypes.

    Strategy:
    - float64 → float32 (halves float memory)
    - int64   → int32   (halves int memory)
    - object columns with low cardinality → category
    """

    def optimize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a memory-optimized copy of the DataFrame.

        Args:
            df: Input DataFrame chunk.

        Returns:
            New DataFrame with reduced-footprint dtypes.
            Values are numerically equivalent within float32 precision.
        """
        if df.empty:
            return df.copy()

        result = df.copy()

        for col in result.columns:
            col_dtype = result[col].dtype

            if col_dtype == "float64":
                result[col] = result[col].astype("float32")

            elif col_dtype == "int64":
                result[col] = result[col].astype("int32")

            elif col_dtype == object or (
                hasattr(pd, "StringDtype") and isinstance(col_dtype, pd.StringDtype)
            ):
                n_unique = result[col].nunique()
                n_total = len(result[col])
                if n_total > 0 and (n_unique / n_total) < _CATEGORY_THRESHOLD:
                    result[col] = result[col].astype("category")

        return result
