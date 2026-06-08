"""Builds a Graphviz DOT representation of a C1 observation result.

Uses the PyScope Observatory palette: deep navy background, sky-blue
accent, neutral grays for edges and labels. Node fill is colored by
architectural regime; node size scales with ACP; edge thickness
scales with DCI.
"""

from __future__ import annotations

from typing import Dict

from .schema import C1Result

# Observatory palette
PALETTE = {
    "bg": "#0A0E17",
    "fg": "#F1F5F9",
    "muted": "#94A3B8",
    "border": "#1E293B",
    "edge": "#475569",
    "accent": "#38BDF8",
    # Regime accent colors (muted, not neon)
    "perfect": "#22C55E",        # green
    "modular": "#38BDF8",        # sky blue
    "layered": "#60A5FA",        # light blue
    "entangled": "#F59E0B",      # amber
    "coupled": "#EF4444",        # red
    "leaky": "#EC4899",          # pink
    "collapsed": "#991B1B",      # deep red
    "mixed": "#A78BFA",          # violet
    "pathological": "#7C2D12",   # dark amber
    "acyclic": "#67E8F9",        # light cyan
    "infrastructure": "#3B82F6", # blue
    "core": "#F97316",           # orange
    "unclassified": "#64748B",   # slate
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
    """Return a DOT string rendering *model* with the Observatory palette."""
    lines: list[str] = [
        "digraph G {",
        '  bgcolor="#0A0E17";',
        '  fontcolor="#F1F5F9";',
        '  fontname="ui-monospace, SF Mono, Consolas, monospace";',
        '  labeljust="l";',
        '  labelloc="t";',
        f'  label=<<FONT POINT-SIZE="18" COLOR="#F1F5F9"><B>PyScope Observation</B></FONT><BR/>'
        f'<FONT POINT-SIZE="10" COLOR="#94A3B8">{model.repository or "unknown"}</FONT>>;',
        '  pad="0.5";',
        '  nodesep="0.6";',
        '  ranksep="0.8";',
        '  splines="true";',
        '  overlap="false";',
        '  node [shape=box, style="rounded,filled", fontname="ui-monospace, SF Mono, Consolas, monospace", fontcolor="#F1F5F9", color="#1E293B"];',
        '  edge [color="#475569", arrowsize="0.7", fontname="ui-monospace, SF Mono, Consolas, monospace"];',
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
        tooltip = f"{node.label} | regime={regime} | acp={node.acp}"
        lines.append(
            f'  "{node.id}" [label=<<B>{node.label}</B><BR/>'
            f'<FONT POINT-SIZE="8" COLOR="#94A3B8">{regime}</FONT>>, '
            f'fillcolor="{color}", color="#1E293B", '
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
        # Highlight strong couplings with the accent color
        edge_color = "#475569"
        if pen > 3.0:
            edge_color = "#EF4444"
        elif pen > 2.0:
            edge_color = "#38BDF8"
        lines.append(
            f'  "{edge.src}" -> "{edge.dst}" [penwidth="{pen}", color="{edge_color}"];'
        )

    lines.append("}")
    return "\n".join(lines)


def build_palette_legend() -> str:
    """Return a small DOT fragment rendering the color legend."""
    lines = ["digraph legend {"]
    lines.append('  bgcolor="#0A0E17"; fontcolor="#F1F5F9";')
    lines.append('  node [shape=box, style="rounded,filled", fontcolor="#F1F5F9", color="#1E293B"];')
    for label, color in NODE_COLOR_MAP.items():
        lines.append(
            f'  "{label}" [label="{label}", fillcolor="{color}"];'
        )
    lines.append("}")
    return "\n".join(lines)


def get_palette() -> Dict[str, str]:
    """Return the full color palette (useful for HTML reports)."""
    return dict(PALETTE)
