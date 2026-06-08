"""
Conftest — Fixtures compartilhadas para testes.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    """Cria um mini-projeto Python para testes."""
    project = tmp_path / "sample_project"
    project.mkdir()

    # __init__.py
    (project / "__init__.py").write_text('"""Sample project."""\n')

    # Módulo core
    core = project / "core"
    core.mkdir()
    (core / "__init__.py").write_text('"""Core module."""\n')
    (core / "models.py").write_text(
        'class User:\n'
        '    def __init__(self, name: str) -> None:\n'
        '        self.name = name\n'
        '\n'
        '    def greet(self) -> str:\n'
        '        return f"Hello, {self.name}"\n'
    )
    (core / "utils.py").write_text(
        'def add(a: int, b: int) -> int:\n'
        '    return a + b\n'
        '\n'
        'def multiply(a: int, b: int) -> int:\n'
        '    return a * b\n'
    )

    # Módulo api
    api = project / "api"
    api.mkdir()
    (api / "__init__.py").write_text('"""API module."""\n')
    (api / "routes.py").write_text(
        'from core.models import User\n'
        '\n'
        'def get_user(name: str) -> User:\n'
        '    return User(name)\n'
    )

    # Módulo services
    services = project / "services"
    services.mkdir()
    (services / "__init__.py").write_text('"""Services module."""\n')
    (services / "auth.py").write_text(
        'from core.models import User\n'
        'from api.routes import get_user\n'
        '\n'
        'def authenticate(name: str) -> bool:\n'
        '    user = get_user(name)\n'
        '    return user is not None\n'
    )

    return project


@pytest.fixture
def sample_graph(sample_project: Path):
    """Constrói um ArchitecturalGraph a partir do mini-projeto."""
    from ags.core.graph.builders import GraphBuilder

    builder = GraphBuilder(str(sample_project))
    return builder.build()


@pytest.fixture
def tmp_database():
    """Cria um banco temporário para testes."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    from ags.storage.database import Database

    db = Database(db_path)
    yield db
    db.close()
    Path(db_path).unlink(missing_ok=True)
