"""Builds a Graphviz DOT representation of a C1 observation result.

Uses the Minimax-inspired dark palette: deep purples, cyans and greens
on near-black backgrounds. Node fill is colored by architectural regime;
node size scales with ACP; edge thickness scales with DCI.
"""

from __future__ import annotations

from typing import Dict

from .schema import C1Result

# Minimax dark palette
PALETTE = {
    "bg": "#0D0D0F",
    "fg": "#E0E0E8",
    "muted": "#8A8A9A",
    "border": "#2A2A35",
    # Regime accent colors
    "perfect": "#10B981",        # emerald
    "modular": "#8B5CF6",        # violet
    "layered": "#06B6D4",        # cyan
    "entangled": "#F59E0B",      # amber
    "coupled": "#EF4444",        # red
    "leaky": "#F472B6",          # pink
    "collapsed": "#DC2626",      # deep red
    "mixed": "#A78BFA",          # light violet
    "pathological": "#7C2D12",   # dark amber
    "acyclic": "#22D3EE",        # light cyan
    "infrastructure": "#3B82F6", # blue
    "core": "#F97316",           # orange
    "unclassified": "#6B7280",   # gray
}

NODE_COLOR_MAP = {
    "perfect": PALETTE["perfect"],
    "modular_small": PALETTE["modular"],
    "modular_large": PALETTE["modular"],
    "layered": PALETTE["layered"],
    "entangled_small": PALETTE["entangled"],
    "entangled_large": PALETTE["entangled"],
    "coupled": PALETTE["coupled"],
    "leaky": PALETTE["leaky"],
    "collapsed": PALETTE["collapsed"],
    "mixed": PALETTE["mixed"],
    "pathological": PALETTE["pathological"],
    "acyclic_dominant": PALETTE["acyclic"],
    "infrastructure": PALETTE["infrastructure"],
    "core": PALETTE["core"],
    "unclassified": PALETTE["unclassified"],
}


def build_dot(model: C1Result) -> str:
    """Return a DOT string rendering *model* with the Minimax dark palette."""
    lines: list[str] = [
        "digraph G {",
        '  bgcolor="#0D0D0F";',
        '  fontcolor="#E0E0E8";',
        '  fontname="ui-monospace, SF Mono, Consolas, monospace";',
        '  labeljust="l";',
        '  labelloc="t";',
        f'  label=<<FONT POINT-SIZE="20" COLOR="#E0E0E8"><B>PyScope Observation</B></FONT><BR/>'
        f'<FONT POINT-SIZE="10" COLOR="#8A8A9A">{model.repository or "unknown"}</FONT>>;',
        '  pad="0.5";',
        '  nodesep="0.6";',
        '  ranksep="0.8";',
        '  splines="true";',
        '  overlap="false";',
        '  node [shape=box, style="rounded,filled", fontname="ui-monospace, SF Mono, Consolas, monospace", fontcolor="#E0E0E8", color="#2A2A35"];',
        '  edge [color="#06B6D4", arrowsize="0.7", fontname="ui-monospace, SF Mono, Consolas, monospace"];',
    ]

    for node in model.nodes:
        regime = (node.regime or "unclassified").lower()
        color = NODE_COLOR_MAP.get(regime, PALETTE["unclassified"])
        size = 1.0
        if node.acp is not None:
            try:
                size = min(2.5, max(0.4, float(node.acp) * 0.6 + 0.4))
            except (TypeError, ValueError):
                size = 1.0
        # Tooltip with details
        tooltip = f"{node.label} | regime={regime} | acp={node.acp}"
        lines.append(
            f'  "{node.id}" [label=<<B>{node.label}</B><BR/>'
            f'<FONT POINT-SIZE="8" COLOR="#8A8A9A">{regime}</FONT>>, '
            f'fillcolor="{color}", color="#2A2A35", '
            f'width="{size}", height="{size * 0.6}", '
            f'tooltip="{tooltip}"];'
        )

    for edge in model.edges:
        pen = 1.0
        if edge.dci is not None:
            try:
                pen = max(0.5, min(4.0, float(edge.dci)))
            except (TypeError, ValueError):
                pen = 1.0
        # Color edges by coupling intensity
        edge_color = "#06B6D4"
        if pen > 3.0:
            edge_color = "#EF4444"
        elif pen > 2.0:
            edge_color = "#F59E0B"
        lines.append(
            f'  "{edge.src}" -> "{edge.dst}" [penwidth="{pen}", color="{edge_color}"];'
        )

    lines.append("}")
    return "\n".join(lines)


def build_palette_legend() -> str:
    """Return a small DOT fragment rendering the color legend."""
    lines = ["digraph legend {"]
    lines.append('  bgcolor="#0D0D0F"; fontcolor="#E0E0E8";')
    lines.append('  node [shape=box, style="rounded,filled", fontcolor="#E0E0E8", color="#2A2A35"];')
    for label, color in NODE_COLOR_MAP.items():
        lines.append(
            f'  "{label}" [label="{label}", fillcolor="{color}"];'
        )
    lines.append("}")
    return "\n".join(lines)


def get_palette() -> Dict[str, str]:
    """Return the full color palette (useful for HTML reports)."""
    return dict(PALETTE)
