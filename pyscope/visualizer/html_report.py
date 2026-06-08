"""Render the PyScope HTML dashboard (Minimax dark theme)."""

from __future__ import annotations

import os
import hashlib
import datetime
try:
    datetime.timezone
except AttributeError:  # pragma: no cover
    pass
from typing import Dict, Optional

from .schema import C1Result

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>PyScope Observation \u2014 {repository}</title>
<style>
  :root {{
    --bg: #0D0D0F;
    --card: #15151B;
    --card-hover: #1A1A22;
    --border: #2A2A35;
    --fg: #E0E0E8;
    --muted: #8A8A9A;
    --accent-purple: #8B5CF6;
    --accent-cyan: #06B6D4;
    --accent-emerald: #10B981;
    --accent-amber: #F59E0B;
    --accent-red: #EF4444;
    --accent-pink: #F472B6;
    --gradient: linear-gradient(135deg, #8B5CF6 0%, #06B6D4 50%, #10B981 100%);
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--fg);
    font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
    line-height: 1.6;
    min-height: 100vh;
    padding: 2rem 1rem;
  }}
  .container {{ max-width: 1280px; margin: 0 auto; }}
  header {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
  }}
  header::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--gradient);
  }}
  header h1 {{
    font-family: ui-monospace, 'SF Mono', Consolas, monospace;
    font-size: 2rem;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
  }}
  header .meta {{
    color: var(--muted);
    font-size: 0.875rem;
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
  }}
  header .meta span strong {{ color: var(--fg); }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }}
  .card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.25rem;
    transition: all 0.2s ease;
    position: relative;
  }}
  .card:hover {{
    background: var(--card-hover);
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(139, 92, 246, 0.1);
  }}
  .card .label {{
    color: var(--muted);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
  }}
  .card .value {{
    font-family: ui-monospace, 'SF Mono', Consolas, monospace;
    font-size: 1.75rem;
    font-weight: 600;
  }}
  .card .value.purple {{ color: var(--accent-purple); }}
  .card .value.cyan {{ color: var(--accent-cyan); }}
  .card .value.emerald {{ color: var(--accent-emerald); }}
  .card .value.amber {{ color: var(--accent-amber); }}
  .card .value.red {{ color: var(--accent-red); }}
  .card .value.pink {{ color: var(--accent-pink); }}
  .card .sub {{
    color: var(--muted);
    font-size: 0.75rem;
    margin-top: 0.25rem;
  }}
  .graph-container {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    overflow: auto;
  }}
  .graph-container h2 {{
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--muted);
    margin-bottom: 1rem;
  }}
  .graph-container svg {{
    max-width: 100%;
    height: auto;
    display: block;
  }}
  .legend {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 1.5rem;
  }}
  .legend h2 {{
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--muted);
    margin-bottom: 1rem;
  }}
  .legend-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 0.5rem;
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    border-radius: 6px;
    background: var(--bg);
  }}
  .swatch {{
    width: 14px; height: 14px;
    border-radius: 3px;
    flex-shrink: 0;
  }}
  .legend-item code {{
    font-family: ui-monospace, 'SF Mono', Consolas, monospace;
    font-size: 0.75rem;
    color: var(--fg);
  }}
  footer {{
    text-align: center;
    color: var(--muted);
    font-size: 0.75rem;
    padding: 1.5rem 0;
    border-top: 1px solid var(--border);
    margin-top: 2rem;
  }}
  footer code {{
    font-family: ui-monospace, 'SF Mono', Consolas, monospace;
    color: var(--accent-cyan);
  }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
  }}
  .pulse {{ animation: pulse 2s ease-in-out infinite; }}
</style>
</head>
<body>
  <div class="container">
    <header>
      <h1>\U0001f52d PyScope Observation</h1>
      <div class="meta">
        <span><strong>Repository:</strong> {repository}</span>
        <span><strong>Observed:</strong> {observed_at}</span>
        <span><strong>Nodes:</strong> {num_nodes}</span>
        <span><strong>Edges:</strong> {num_edges}</span>
      </div>
    </header>

    <div class="grid">
      {metric_cards}
    </div>

    <div class="graph-container">
      <h2>Architectural Graph</h2>
      {svg_content}
    </div>

    <div class="legend">
      <h2>Regime Color Legend</h2>
      <div class="legend-grid">
        {legend_items}
      </div>
    </div>

    <footer>
      Generated by <code>PyScope</code> \u00b7 {generated_at} \u00b7 hash <code>{file_hash}</code>
    </footer>
  </div>
</body>
</html>
"""

METRIC_LABELS = {
    "cross_domain_ratio": ("Cross-Domain Ratio", "purple"),
    "intra_domain_ratio": ("Intra-Domain Ratio", "cyan"),
    "leakage": ("Boundary Leakage", "pink"),
    "cycle_density": ("Cycle Density", "amber"),
    "observation_quality": ("Observation Quality", "emerald"),
    "total_nodes": ("Total Nodes", "cyan"),
    "total_edges": ("Total Edges", "cyan"),
    "cross_domain_edges": ("Cross-Domain Edges", "purple"),
    "intra_domain_edges": ("Intra-Domain Edges", "cyan"),
    "unknown_unresolved_edges": ("Unresolved Edges", "amber"),
    "unknown_dynamic_edges": ("Dynamic Edges", "amber"),
    "regime": ("Detected Regime", "emerald"),
    "distance_1": ("Distance to Nearest", "pink"),
    "margin": ("Classification Margin", "amber"),
    "confidence": ("Classification Confidence", "emerald"),
    "nearest_regime": ("Nearest Regime", "cyan"),
    "second_nearest_regime": ("Second Nearest", "muted"),
}

REGIME_COLORS = {
    "perfect": "#10B981",
    "modular_small": "#8B5CF6",
    "modular_large": "#8B5CF6",
    "layered": "#06B6D4",
    "entangled_small": "#F59E0B",
    "entangled_large": "#F59E0B",
    "coupled": "#EF4444",
    "leaky": "#F472B6",
    "collapsed": "#DC2626",
    "mixed": "#A78BFA",
    "pathological": "#7C2D12",
    "acyclic_dominant": "#22D3EE",
}


def _format_value(v) -> str:
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def _metric_card(key: str, value) -> str:
    label, css_class = METRIC_LABELS.get(key, (key.replace("_", " ").title(), "purple"))
    return (
        f'<div class="card">'
        f'<div class="label">{label}</div>'
        f'<div class="value {css_class}">{_format_value(value)}</div>'
        f'</div>'
    )


def _legend_item(label: str, color: str) -> str:
    return (
        f'<div class="legend-item">'
        f'<div class="swatch" style="background: {color};"></div>'
        f'<code>{label}</code>'
        f'</div>'
    )


def write_html_report(
    output_dir: str,
    artifacts: Dict[str, str],
    metrics: dict,
) -> str:
    """Render the PyScope dashboard HTML to ``<output_dir>/index.html``.

    *artifacts* must contain ``"svg"`` with the path to the rendered SVG.
    *metrics* is the dictionary of metrics/regime info to render as cards.
    """
    os.makedirs(output_dir, exist_ok=True)
    html_path = os.path.join(output_dir, "index.html")

    svg_content = ""
    svg_path = artifacts.get("svg", "")
    if svg_path and os.path.exists(svg_path):
        try:
            with open(svg_path, "r", encoding="utf-8") as f:
                svg_content = f.read()
        except OSError:
            svg_content = '<p style="color: var(--accent-red);">SVG unavailable</p>'

    metric_cards = "\n".join(_metric_card(k, v) for k, v in metrics.items())
    legend_items = "\n".join(
        _legend_item(label, color) for label, color in REGIME_COLORS.items()
    )

    repository = metrics.get("repository", "unknown")
    observed_at = metrics.get("observed_at", "unknown")
    num_nodes = metrics.get("total_nodes", len(artifacts.get("nodes", [])))
    num_edges = metrics.get("total_edges", len(artifacts.get("edges", [])))

    generated_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    file_hash = hashlib.sha256(svg_content.encode("utf-8")).hexdigest()[:12]

    html = HTML_TEMPLATE.format(
        repository=repository,
        observed_at=observed_at,
        num_nodes=num_nodes,
        num_edges=num_edges,
        metric_cards=metric_cards,
        svg_content=svg_content,
        legend_items=legend_items,
        generated_at=generated_at,
        file_hash=file_hash,
    )

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    return html_path


def write_report_from_c1(
    output_dir: str,
    c1: C1Result,
    svg_path: Optional[str] = None,
) -> str:
    """Convenience: build the dashboard directly from a ``C1Result``."""
    metrics = dict(c1.metrics or {})
    metrics.setdefault("repository", c1.repository or "unknown")
    metrics.setdefault("observed_at", c1.observed_at or "unknown")
    metrics.setdefault("total_nodes", len(c1.nodes))
    metrics.setdefault("total_edges", len(c1.edges))

    artifacts: Dict[str, str] = {"nodes": [n.id for n in c1.nodes]}
    if svg_path:
        artifacts["svg"] = svg_path
    return write_html_report(output_dir, artifacts, metrics)
