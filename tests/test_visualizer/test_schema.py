import os
from pyscope.visualizer.schema import C1Result


def test_schema_reading():
    path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "c1_example.json")
    path = os.path.normpath(path)
    model = C1Result.from_json(path)
    assert model.repository == "requests"
    assert len(model.nodes) == 3
