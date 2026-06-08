from .schema import C1Result


def build_dot(model: C1Result) -> str:
    lines = ["digraph G {", "  rankdir=LR;", "  node [shape=box];"]

    color_map = {
        "layered": "#4CAF50",
        "infrastructure": "#2196F3",
        "core": "#FF9800",
        "unclassified": "#9E9E9E",
    }

    for node in model.nodes:
        color = color_map.get(node.regime, "#9E9E9E")
        size = 1.0
        if node.acp is not None:
            try:
                size = min(2.0, max(0.3, float(node.acp) * 0.5))
            except Exception:
                size = 1.0
        lines.append(
            f'  "{node.id}" [label="{node.label}", style=filled, fillcolor="{color}", width="{size}", height="{size}"]'
        )

    for edge in model.edges:
        pen = 1.0
        if edge.dci is not None:
            try:
                pen = max(0.5, float(edge.dci))
            except Exception:
                pen = 1.0
        lines.append(f'  "{edge.src}" -> "{edge.dst}" [penwidth="{pen}"]')

    lines.append("}")
    return "\n".join(lines)
