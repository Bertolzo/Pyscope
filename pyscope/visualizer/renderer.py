import os


def render_dot_to_files(dot_source: str, output_dir: str, base_name: str = "graph") -> dict:
    os.makedirs(output_dir, exist_ok=True)
    dot_path = os.path.join(output_dir, base_name + ".dot")
    svg_path = os.path.join(output_dir, base_name + ".svg")
    png_path = os.path.join(output_dir, base_name + ".png")

    with open(dot_path, "w", encoding="utf-8") as f:
        f.write(dot_source)

    result = {"dot": dot_path}

    try:
        import graphviz

        g = graphviz.Source(dot_source)
        g.format = "svg"
        g.render(filename=os.path.join(output_dir, base_name), cleanup=False)
        if os.path.exists(svg_path):
            result["svg"] = svg_path
        g.format = "png"
        g.render(filename=os.path.join(output_dir, base_name), cleanup=False)
        if os.path.exists(png_path):
            result["png"] = png_path
    except Exception:
        pass

    return result
