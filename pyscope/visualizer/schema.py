from dataclasses import dataclass
from typing import List, Optional
import json


@dataclass
class Node:
    id: str
    label: str
    acp: Optional[float] = None
    regime: Optional[str] = None


@dataclass
class Edge:
    src: str
    dst: str
    dci: Optional[float] = None


@dataclass
class C1Result:
    repository: Optional[str]
    observed_at: Optional[str]
    nodes: List[Node]
    edges: List[Edge]
    metrics: dict

    @classmethod
    def from_json(cls, path: str) -> "C1Result":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        nodes = [Node(**n) for n in data.get("nodes", [])]
        edges = [Edge(**e) for e in data.get("edges", [])]
        return cls(
            repository=data.get("repository"),
            observed_at=data.get("observed_at"),
            nodes=nodes,
            edges=edges,
            metrics=data.get("metrics", {}),
        )
