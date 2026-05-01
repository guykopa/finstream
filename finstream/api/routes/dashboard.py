import os

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, text

from finstream.report.dashboard_renderer import DashboardData, DashboardRenderer

router = APIRouter(tags=["dashboard"])

_renderer = DashboardRenderer()


def _load_dashboard_data() -> DashboardData:
    """Query PostgreSQL and return aggregated data for the dashboard."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return DashboardData()

    engine = create_engine(database_url)
    data = DashboardData()

    with engine.connect() as conn:
        row = conn.execute(text(
            "SELECT COUNT(*), COALESCE(SUM(amount), 0),"
            " COUNT(DISTINCT entity), COUNT(DISTINCT date)"
            " FROM transactions"
        )).fetchone()
        if row is not None:
            data.total_transactions = int(row[0])
            data.total_amount_eur = float(row[1])
            data.unique_entities = int(row[2])
            data.trading_days = int(row[3])

        rows = conn.execute(text(
            "SELECT date::text, SUM(amount) FROM transactions"
            " GROUP BY date ORDER BY date"
        )).fetchall()
        data.dates = [r[0] for r in rows]
        data.daily_volumes = [float(r[1]) for r in rows]

        rows = conn.execute(text(
            "SELECT entity, SUM(amount) AS total FROM transactions"
            " GROUP BY entity ORDER BY total DESC LIMIT 10"
        )).fetchall()
        data.top_entities = [r[0] for r in rows]
        data.top_amounts = [float(r[1]) for r in rows]

        rows = conn.execute(text(
            "SELECT source, COUNT(*) FROM transactions GROUP BY source ORDER BY COUNT(*) DESC"
        )).fetchall()
        data.sources = [r[0] for r in rows]
        data.source_counts = [int(r[1]) for r in rows]

    return data


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    """Serve the interactive BI dashboard with real transaction data from PostgreSQL."""
    data = _load_dashboard_data()
    html = _renderer.generate(data)
    return HTMLResponse(content=html)
