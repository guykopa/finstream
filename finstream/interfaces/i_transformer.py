from abc import ABC, abstractmethod

import pandas as pd


class ITransformer(ABC):
    """Contract for a single stateless DataFrame transformation."""

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply transformation to a DataFrame chunk.

        Args:
            df: Input DataFrame chunk.

        Returns:
            Transformed DataFrame, same or fewer rows, same columns.

        Raises:
            TransformationError: if transformation fails.
        """

    @abstractmethod
    def transformer_name(self) -> str:
        """Return the name of this transformer for logging."""
