import os
from pyscope.visualizer.schema import C1Result
from pyscope.visualizer.graphviz_builder import build_dot


def test_build_dot():
    path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "c1_example.json")
    path = os.path.normpath(path)
    model = C1Result.from_json(path)
    dot = build_dot(model)
    assert "digraph" in dot
    assert "requests.api" in dot
