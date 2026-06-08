import os
from typing import Dict


def write_html_report(output_dir: str, artifacts: Dict[str, str], metrics: dict) -> str:
    os.makedirs(output_dir, exist_ok=True)
    html_path = os.path.join(output_dir, "index.html")

    svg_content = ""
    if "svg" in artifacts:
        try:
            with open(artifacts["svg"], "r", encoding="utf-8") as f:
                svg_content = f.read()
        except Exception:
            svg_content = ""

    table_rows = "\n".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in metrics.items())

    html = f"""
<html>
<head><meta charset="utf-8"><title>PyScope Visualizer Report</title></head>
<body>
<h1>PyScope Visualizer</h1>
<div id="svg">{svg_content}</div>
<h2>Metrics</h2>
<table border="1">{table_rows}</table>
</body>
</html>
"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    return html_path
