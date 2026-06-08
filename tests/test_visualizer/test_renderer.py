import os
from pyscope.visualizer.schema import C1Result
from pyscope.visualizer.graphviz_builder import build_dot
from pyscope.visualizer.renderer import render_dot_to_files
from pyscope.visualizer.html_report import write_html_report


def test_render_and_report(tmp_path):
    path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "c1_example.json")
    path = os.path.normpath(path)
    model = C1Result.from_json(path)
    dot = build_dot(model)
    out = tmp_path / "out"
    out.mkdir()
    artifacts = render_dot_to_files(dot, str(out))
    assert "dot" in artifacts
    html = write_html_report(str(out), artifacts, model.metrics)
    assert os.path.exists(html)
