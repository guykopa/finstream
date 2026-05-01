from __future__ import annotations

import json
from dataclasses import dataclass, field

from finstream.interfaces.i_report_generator import IReportGenerator


@dataclass
class DashboardData:
    """Aggregated data for the BI dashboard."""
    total_transactions: int = 0
    total_amount_eur: float = 0.0
    unique_entities: int = 0
    trading_days: int = 0
    dates: list[str] = field(default_factory=list)
    daily_volumes: list[float] = field(default_factory=list)
    top_entities: list[str] = field(default_factory=list)
    top_amounts: list[float] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    source_counts: list[int] = field(default_factory=list)


_HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>finstream — BI Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
  <style>
    *{{ box-sizing:border-box; margin:0; padding:0; }}
    body{{ font-family:'Segoe UI',sans-serif; background:#0f172a; color:#e2e8f0; padding:2rem; }}
    h1{{ color:#38bdf8; font-size:1.8rem; margin-bottom:.25rem; }}
    .subtitle{{ color:#64748b; font-size:.9rem; margin-bottom:2rem; }}
    .kpis{{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:1rem; margin-bottom:2rem; }}
    .kpi{{ background:#1e293b; border-radius:12px; padding:1.25rem 1.5rem; border-left:4px solid #38bdf8; }}
    .kpi .val{{ font-size:2rem; font-weight:700; color:#38bdf8; }}
    .kpi .lbl{{ font-size:.75rem; color:#94a3b8; text-transform:uppercase; letter-spacing:.05em; margin-top:.25rem; }}
    .charts{{ display:grid; grid-template-columns:repeat(auto-fit,minmax(420px,1fr)); gap:1.5rem; }}
    .card{{ background:#1e293b; border-radius:12px; padding:1.5rem; }}
    .card h2{{ font-size:.85rem; color:#94a3b8; text-transform:uppercase; letter-spacing:.05em; margin-bottom:1rem; }}
    .chart-wrap{{ position:relative; height:260px; }}
  </style>
</head>
<body>
  <h1>finstream BI Dashboard</h1>
  <p class="subtitle">Données financières en temps réel — {total_transactions} transactions • {trading_days} jours de trading</p>

  <div class="kpis">
    <div class="kpi"><div class="val">{total_transactions:,}</div><div class="lbl">Transactions</div></div>
    <div class="kpi"><div class="val">{total_amount_eur}</div><div class="lbl">Volume total (EUR)</div></div>
    <div class="kpi"><div class="val">{unique_entities}</div><div class="lbl">Entités uniques</div></div>
    <div class="kpi"><div class="val">{trading_days}</div><div class="lbl">Jours de trading</div></div>
  </div>

  <div class="charts">
    <div class="card" style="grid-column:1/-1">
      <h2>Volume EUR par jour de trading</h2>
      <div class="chart-wrap"><canvas id="dailyChart"></canvas></div>
    </div>
    <div class="card">
      <h2>Top 10 entités par volume EUR</h2>
      <div class="chart-wrap"><canvas id="entitiesChart"></canvas></div>
    </div>
    <div class="card">
      <h2>Répartition par source de données</h2>
      <div class="chart-wrap"><canvas id="sourcesChart"></canvas></div>
    </div>
  </div>

  <script>
    const dates         = {dates_json};
    const dailyVolumes  = {daily_volumes_json};
    const topEntities   = {top_entities_json};
    const topAmounts    = {top_amounts_json};
    const sources       = {sources_json};
    const sourceCounts  = {source_counts_json};

    const gridColor = '#334155';
    const tickColor = '#94a3b8';
    const legendColor = '#e2e8f0';

    // Daily volume line chart
    new Chart(document.getElementById('dailyChart'), {{
      type: 'line',
      data: {{
        labels: dates,
        datasets: [{{
          label: 'Volume EUR',
          data: dailyVolumes,
          borderColor: '#38bdf8',
          backgroundColor: 'rgba(56,189,248,.1)',
          fill: true,
          tension: .3,
          pointRadius: 4,
          pointBackgroundColor: '#38bdf8',
        }}]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        scales: {{
          x: {{ grid: {{ color: gridColor }}, ticks: {{ color: tickColor, maxRotation: 45 }} }},
          y: {{ grid: {{ color: gridColor }}, ticks: {{ color: tickColor,
               callback: v => '€' + (v >= 1e6 ? (v/1e6).toFixed(1)+'M' : v >= 1e3 ? (v/1e3).toFixed(0)+'K' : v) }} }}
        }},
        plugins: {{ legend: {{ labels: {{ color: legendColor }} }} }}
      }}
    }});

    // Top entities horizontal bar
    new Chart(document.getElementById('entitiesChart'), {{
      type: 'bar',
      data: {{
        labels: topEntities,
        datasets: [{{
          label: 'Volume EUR',
          data: topAmounts,
          backgroundColor: 'rgba(56,189,248,.7)',
          borderColor: '#38bdf8',
          borderWidth: 1,
          borderRadius: 4,
        }}]
      }},
      options: {{
        indexAxis: 'y',
        responsive: true, maintainAspectRatio: false,
        scales: {{
          x: {{ grid: {{ color: gridColor }}, ticks: {{ color: tickColor,
               callback: v => '€' + (v >= 1e3 ? (v/1e3).toFixed(0)+'K' : v) }} }},
          y: {{ grid: {{ display: false }}, ticks: {{ color: tickColor }} }}
        }},
        plugins: {{ legend: {{ display: false }} }}
      }}
    }});

    // Sources doughnut
    const sourceColors = ['#38bdf8','#4ade80','#fbbf24','#f87171','#a78bfa','#fb923c'];
    new Chart(document.getElementById('sourcesChart'), {{
      type: 'doughnut',
      data: {{
        labels: sources,
        datasets: [{{
          data: sourceCounts,
          backgroundColor: sourceColors.slice(0, sources.length),
          borderWidth: 0,
        }}]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ position: 'right', labels: {{ color: legendColor, padding: 16 }} }} }}
      }}
    }});
  </script>
</body>
</html>"""


class DashboardRenderer(IReportGenerator):
    """Render aggregated transaction data as a self-contained HTML dashboard."""

    def generate(self, data: DashboardData) -> str:  # type: ignore[override]
        """Build the HTML dashboard from aggregated transaction data.

        Args:
            data: Aggregated statistics and chart series from PostgreSQL.

        Returns:
            Complete HTML string ready to be served by FastAPI.
        """
        if data.total_amount_eur >= 1_000_000:
            amount_str = f"€{data.total_amount_eur / 1_000_000:.1f}M"
        elif data.total_amount_eur >= 1_000:
            amount_str = f"€{data.total_amount_eur / 1_000:.0f}K"
        else:
            amount_str = f"€{data.total_amount_eur:.0f}"

        return _HTML.format(
            total_transactions=data.total_transactions,
            total_amount_eur=amount_str,
            unique_entities=data.unique_entities,
            trading_days=data.trading_days,
            dates_json=json.dumps(data.dates),
            daily_volumes_json=json.dumps([round(v, 2) for v in data.daily_volumes]),
            top_entities_json=json.dumps(data.top_entities),
            top_amounts_json=json.dumps([round(v, 2) for v in data.top_amounts]),
            sources_json=json.dumps(data.sources),
            source_counts_json=json.dumps(data.source_counts),
        )
