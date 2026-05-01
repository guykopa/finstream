from datetime import date
from typing import Iterator

import httpx
import pandas as pd

from finstream.domain.exceptions import DataSourceUnavailableError
from finstream.interfaces.i_data_source import IDataSource


class RestAPISource(IDataSource):
    """Read financial transactions from a paginated REST API.

    Each API page becomes one DataFrame chunk. Pagination stops when
    the API returns an empty result or signals the last page.
    """

    def __init__(self, base_url: str, api_key: str, timeout: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout

    def read_chunks(
        self,
        business_date: date,
        chunk_size: int = 10_000,
    ) -> Iterator[pd.DataFrame]:
        """Fetch paginated transactions for a given business date.

        Args:
            business_date: The date to fetch transactions for.
            chunk_size: Page size requested from the API.

        Yields:
            DataFrame chunks, one per API page.

        Raises:
            DataSourceUnavailableError: if the API is unreachable.
        """
        headers = {"Authorization": f"Bearer {self._api_key}"}
        page = 1

        try:
            with httpx.Client(timeout=self._timeout) as client:
                while True:
                    response = client.get(
                        f"{self._base_url}/transactions",
                        headers=headers,
                        params={
                            "date": business_date.isoformat(),
                            "page": page,
                            "page_size": chunk_size,
                        },
                    )
                    response.raise_for_status()
                    records = response.json().get("data", [])

                    if not records:
                        break

                    yield pd.DataFrame(records)
                    page += 1

        except httpx.HTTPError as exc:
            raise DataSourceUnavailableError(self._base_url) from exc

    def is_available(self) -> bool:
        """Return True if the API health endpoint responds successfully."""
        try:
            response = httpx.get(
                f"{self._base_url}/health",
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=self._timeout,
            )
            return response.is_success
        except httpx.HTTPError:
            return False
