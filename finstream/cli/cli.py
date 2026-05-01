"""finstream CLI — trigger the ETL pipeline from the command line.

Usage:
    python -m finstream.cli run --date 2024-01-15 --source csv --file data.csv
    python -m finstream.cli run --date 2024-01-15 --source fake
    python -m finstream.cli health
"""
import argparse
import sys
from datetime import date

from finstream.monitoring.logger import StructuredLogger

_logger = StructuredLogger("finstream.cli")


def _cmd_run(args: argparse.Namespace) -> int:
    """Execute the ETL pipeline for a given business date."""
    from tests.conftest import FakeDataSource, FakeDataStorage
    from finstream.pipeline.etl_pipeline import ETLPipeline
    from finstream.domain.exceptions import QualityGateError, DataSourceUnavailableError

    try:
        business_date = date.fromisoformat(args.date)
    except ValueError:
        print(f"Error: invalid date '{args.date}'. Use YYYY-MM-DD format.", file=sys.stderr)
        return 1

    _logger.info("CLI pipeline run started", date=str(business_date))

    try:
        if args.source == "csv":
            from finstream.extract.csv_source import CSVSource
            source = CSVSource(args.file)
        else:
            import pandas as pd
            import numpy as np
            rng = np.random.default_rng(42)
            n = 1_000
            sample = pd.DataFrame({
                "id":       [f"tx-{i:06d}" for i in range(n)],
                "amount":   rng.uniform(10.0, 5_000.0, n).tolist(),
                "currency": rng.choice(["EUR", "USD", "GBP", "CHF"], n).tolist(),
                "entity":   [f"E{i % 10:03d}" for i in range(n)],
                "date":     [str(business_date)] * n,
                "source":   ["fake"] * n,
            })
            source = FakeDataSource(sample)

        storage = FakeDataStorage()
        pipeline = ETLPipeline(
            source=source,
            storage=storage,
            quality_gate_threshold=args.quality_gate,
            chunk_size=args.chunk_size,
        )
        report = pipeline.run(business_date)

        print(f"Run ID        : {report.run_id}")
        print(f"Status        : {report.status.value}")
        print(f"Total records : {report.total_records:,}")
        print(f"Clean records : {report.clean_records:,}")
        print(f"Quality score : {report.quality_score:.1f}%")
        print(f"Duration      : {report.duration_seconds:.3f}s")
        print(f"Chunks        : {report.chunk_count}")
        return 0

    except QualityGateError as exc:
        print(f"Quality gate failed: {exc}", file=sys.stderr)
        return 2
    except DataSourceUnavailableError as exc:
        print(f"Data source unavailable: {exc}", file=sys.stderr)
        return 3


def _cmd_health(_args: argparse.Namespace) -> int:
    """Print a simple health status."""
    print("finstream: OK")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="finstream",
        description="finstream ETL pipeline CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Execute the ETL pipeline")
    run_p.add_argument("--date", required=True, help="Business date (YYYY-MM-DD)")
    run_p.add_argument(
        "--source", choices=["fake", "csv"], default="fake",
        help="Data source (default: fake)"
    )
    run_p.add_argument("--file", default="data.csv", help="CSV file path (for --source csv)")
    run_p.add_argument("--chunk-size", type=int, default=10_000, dest="chunk_size")
    run_p.add_argument("--quality-gate", type=float, default=80.0, dest="quality_gate")
    run_p.set_defaults(func=_cmd_run)

    health_p = sub.add_parser("health", help="Print health status")
    health_p.set_defaults(func=_cmd_health)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
