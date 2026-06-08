#!/usr/bin/env python3
"""Helper script for phased AGS validation.

This tool is intended to support the validation phases described in
`docs/AGS_VALIDATION_PHASED_PLAN.md`.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple

from ags.orchestrator import AGS
from ags.core.graph.builders import GraphBuilder

EXCLUDE_DIRS = frozenset({
    "venv", ".venv", "__pycache__", ".git", ".pytest_cache",
    "node_modules", "dist", "build", ".mypy_cache", ".ruff_cache",
    "eggs", "*.egg-info", ".tox", ".nox",
})


def collect_python_files(project_path: Path) -> List[Path]:
    files: List[Path] = []
    for file_path in project_path.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in file_path.parts):
            continue
        files.append(file_path)
    files.sort()
    return files


def parse_imports_from_file(file_path: Path) -> List[Dict[str, Any]]:
    imports: List[Dict[str, Any]] = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError):
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append({
                    "type": "import",
                    "module": name.name,
                    "name": "",
                    "level": 0,
                    "line": getattr(node, "lineno", 0),
                })
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                module = "." * node.level + module
            for alias in node.names:
                imports.append({
                    "type": "from",
                    "module": module,
                    "name": alias.name,
                    "level": node.level,
                    "line": getattr(node, "lineno", 0),
                })
    return imports


def collect_ast_imports(project_path: Path) -> List[Dict[str, Any]]:
    imports: List[Dict[str, Any]] = []
    for file_path in collect_python_files(project_path):
        file_imports = parse_imports_from_file(file_path)
        for imp in file_imports:
            imp["file"] = str(file_path)
            imports.append(imp)
    return imports


def export_ast_imports(project_path: Path, output_path: Path) -> None:
    imports = collect_ast_imports(project_path)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(imports, f, indent=2, ensure_ascii=False)
    print(f"✅ AST imports exported: {output_path}")


def export_ags_report(project_path: Path, db_path: Path, report_path: Path, graph_path: Optional[Path]) -> None:
    with AGS(str(project_path), db_path=str(db_path)) as ags:
        report = ags.analyze()
        ags.export_json(str(report_path))
        print(f"✅ AGS report exported: {report_path}")
        if graph_path is not None:
            graph_dict = ags.graph.to_dict()
            with graph_path.open("w", encoding="utf-8") as f:
                json.dump(graph_dict, f, indent=2, ensure_ascii=False)
            print(f"✅ AGS graph exported: {graph_path}")


def export_ags_graph(project_path: Path, graph_path: Path) -> None:
    builder = GraphBuilder(str(project_path))
    graph = builder.build()
    with graph_path.open("w", encoding="utf-8") as f:
        json.dump(graph.to_dict(), f, indent=2, ensure_ascii=False)
    print(f"✅ AGS graph JSON exported: {graph_path}")


def compare_imports(project_path: Path, ags_graph_path: Path, ast_imports_path: Path, output_path: Path) -> None:
    with ags_graph_path.open("r", encoding="utf-8") as f:
        graph = json.load(f)

    with ast_imports_path.open("r", encoding="utf-8") as f:
        ast_imports = json.load(f)

    project_modules = detect_project_modules(project_path)
    resolved_edges = set()
    for edge in graph.get("edges", []):
        if edge.get("import_type") in ("import", "from", "dynamic"):
            resolved_edges.add((edge.get("from"), edge.get("to")))

    unresolved_candidates: List[Dict[str, Any]] = []
    for imp in ast_imports:
        module_name = imp.get("module", "")
        if not module_name or module_name.startswith("."):
            continue
        top_module = module_name.split(".")[0]
        if top_module not in project_modules:
            continue
        if not file_imported_by_graph(project_path, imp, resolved_edges):
            unresolved_candidates.append(imp)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump({
            "project": str(project_path),
            "unresolved_project_imports": unresolved_candidates,
            "unresolved_count": len(unresolved_candidates),
        }, f, indent=2, ensure_ascii=False)

    print(f"✅ Import comparison exported: {output_path}")
    print(f"Unresolved project imports: {len(unresolved_candidates)}")


def detect_project_modules(project_path: Path) -> Set[str]:
    modules: Set[str] = set()
    for item in project_path.iterdir():
        if not item.is_dir():
            continue
        if item.name.startswith(".") or item.name.startswith("__"):
            continue
        if (item / "__init__.py").exists() or any(item.rglob("*.py")):
            modules.add(item.name)
    return modules


def normalize_graph_node(node: str, project_path: Path) -> str:
    if node.startswith("module:"):
        return node[len("module:"):]

    try:
        resolved_project = project_path.resolve()
        path = Path(node)
        if path.is_absolute():
            path = path.relative_to(resolved_project)
        if path.name == "__init__.py":
            path = path.parent
        return ".".join(path.with_suffix("").parts)
    except Exception:
        return node


def file_imported_by_graph(project_path: Path, imp: Dict[str, Any], edges: Set[Tuple[str, str]]) -> bool:
    source = imp.get("file")
    if not source:
        return False
    source_path = Path(source)
    module_name = imp.get("module", "")
    if module_name.startswith("."):
        return False

    target_module = module_name
    source_module = normalize_graph_node(str(source_path), project_path)

    for from_path, to_path in edges:
        from_module = normalize_graph_node(str(from_path), project_path)
        to_module = normalize_graph_node(str(to_path), project_path)

        if from_module == source_module and (to_module == target_module or to_module.startswith(target_module + ".") or target_module.startswith(to_module + ".") or target_module in to_module):
            return True

    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AGS validation helper for phased comparison with external tools."
    )
    subparsers = parser.add_subparsers(dest="command")

    analyze = subparsers.add_parser("analyze", help="Run AGS and export report and optional graph JSON.")
    analyze.add_argument("project", type=Path, help="Path to target Python project.")
    analyze.add_argument("--db", type=Path, default=Path("ags_validation.db"), help="SQLite DB path.")
    analyze.add_argument("--report", type=Path, default=Path("ags_validation_report.json"), help="AGS report JSON output.")
    analyze.add_argument("--graph", type=Path, default=None, help="Optional AGS graph JSON output.")

    graph = subparsers.add_parser("export-graph", help="Export AGS graph JSON without running the full analysis pipeline.")
    graph.add_argument("project", type=Path, help="Path to target Python project.")
    graph.add_argument("--output", type=Path, default=Path("ags_graph.json"), help="Graph JSON output file.")

    imports = subparsers.add_parser("extract-imports", help="Export AST import statements for the project.")
    imports.add_argument("project", type=Path, help="Path to target Python project.")
    imports.add_argument("--output", type=Path, default=Path("ast_imports.json"), help="AST imports JSON output file.")

    compare = subparsers.add_parser("compare-imports", help="Compare AST imports against AGS graph resolution.")
    compare.add_argument("project", type=Path, help="Path to target Python project.")
    compare.add_argument("--ags-graph", type=Path, default=Path("ags_graph.json"), help="AGS graph JSON file.")
    compare.add_argument("--ast-imports", type=Path, default=Path("ast_imports.json"), help="AST imports JSON file.")
    compare.add_argument("--output", type=Path, default=Path("import_comparison.json"), help="Output comparison JSON file.")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "analyze":
        export_ags_report(args.project, args.db, args.report, args.graph)
        return 0

    if args.command == "export-graph":
        export_ags_graph(args.project, args.output)
        return 0

    if args.command == "extract-imports":
        export_ast_imports(args.project, args.output)
        return 0

    if args.command == "compare-imports":
        compare_imports(args.project, args.ags_graph, args.ast_imports, args.output)
        return 0

    print("No command specified. Use --help for available commands.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
