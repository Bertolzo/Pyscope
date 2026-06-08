from .schema import C1Result


def build_dot(model: C1Result) -> str:
    lines = ["digraph G {", "  rankdir=LR;", "  node [shape=box];"]

    color_map = {
        "layered": "#4CAF50",
        "infrastructure": "#2196F3",
        "core": "#FF9800",
        "unclassified": "#9E9E9E",
    }

    for n in model.nodes:
        color = color_map.get(n.regime, "#9E9E9E")
        size = 1.0
        if n.acp is not None:
            try:
                size = min(2.0, max(0.3, float(n.acp) * 0.5))
            except Exception:
                size = 1.0
        lines.append(
            f'  "{n.id}" [label="{n.label}", style=filled, fillcolor="{color}", width="{size}", height="{size}"]'
        )

    for e in model.edges:
        pen = 1.0
        if e.dci is not None:
            try:
                pen = max(0.5, float(e.dci))
            except Exception:
                pen = 1.0
        lines.append(f'  "{e.src}" -> "{e.dst}" [penwidth="{pen}"]')

    lines.append("}")
    return "\n".join(lines)
