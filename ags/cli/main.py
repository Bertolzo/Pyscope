"""
AGS v2 CLI — Interface de linha de comando.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ags import __version__
from ags.orchestrator import AGS

app = typer.Typer(
    name="ags",
    help="AGS v2 — Architectural Governance System",
    add_completion=False,
)
console = Console()


@app.command()
def analyze(
    project_path: str = typer.Argument(..., help="Caminho do projeto Python"),
    db: str = typer.Option("ags_data.db", "--db", help="Caminho do banco SQLite"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Exportar relatório JSON"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Arquivo de configuração JSON"),
    fail_on_critical: bool = typer.Option(False, "--fail-on-critical", help="Falhar se colapsando"),
) -> None:
    """Analisa um projeto Python e gera relatório arquitetural."""
    project = Path(project_path).resolve()
    if not project.exists():
        console.print(f"[red]❌ Projeto não encontrado: {project}[/red]")
        raise typer.Exit(1)

    config_data = None
    if config:
        config_path = Path(config)
        if config_path.exists():
            with open(config_path) as f:
                config_data = json.load(f)

    with AGS(str(project), config=config_data, db_path=db) as ags:
        report = ags.analyze()
        ags.print_report()

        if output:
            ags.export_json(output)

        if fail_on_critical and ags.guardian and not ags.guardian.merge_allowed:
            console.print("\n[red]❌ MERGE BLOQUEADO: Regressão arquitetural detectada.[/red]")
            raise typer.Exit(1)

        if ags.guardian:
            raise typer.Exit(ags.guardian.exit_code)


@app.command()
def history(
    db: str = typer.Option("ags_data.db", "--db", help="Caminho do banco SQLite"),
    limit: int = typer.Option(20, "--limit", "-n", help="Número de snapshots"),
) -> None:
    """Mostra histórico de snapshots."""
    from ags.storage.database import Database
    from ags.storage.repositories.snapshot_repo import SnapshotRepository

    with Database(db) as database:
        repo = SnapshotRepository(database)
        history = repo.get_history(limit)

        if not history:
            console.print("[yellow]Nenhum snapshot encontrado.[/yellow]")
            return

        table = Table(title=f"Últimos {len(history)} Snapshots")
        table.add_column("ID", style="dim")
        table.add_column("Timestamp")
        table.add_column("CRI", justify="right")
        table.add_column("Entropy", justify="right")
        table.add_column("AGP", justify="right")
        table.add_column("Cycles", justify="right")

        for row in history:
            table.add_row(
                str(row["id"]),
                row["timestamp"][:19],
                f"{row['cri_score']:.1f}",
                f"{row['architectural_entropy']:.1f}",
                f"{row['agp_score']:.1f}",
                str(row["cycle_count"]),
            )

        console.print(table)


@app.command()
def forecast(
    db: str = typer.Option("ags_data.db", "--db", help="Caminho do banco SQLite"),
) -> None:
    """Mostra previsão de evolução arquitetural."""
    from ags.storage.database import Database
    from ags.storage.repositories.snapshot_repo import SnapshotRepository

    with Database(db) as database:
        repo = SnapshotRepository(database)
        history = repo.get_history_for_forecast(limit=100)

        if len(history) < 2:
            console.print("[yellow]Histórico insuficiente para previsão (mínimo 2 snapshots).[/yellow]")
            return

        from ags.core.structural.snapshot import StructuralSnapshot

        last = history[-1]
        try:
            full = json.loads(last.get("full_snapshot", "{}"))
            structural = StructuralSnapshot(**full)
        except Exception:
            console.print("[red]Erro ao carregar último snapshot.[/red]")
            return

        from ags.core.coupling.snapshot import CouplingReport
        from ags.intelligence.evolution.analyzer import EvolutionAnalyzer
        from ags.intelligence.prediction.engine import PredictionEngine

        coupling = CouplingReport()
        evolution = EvolutionAnalyzer().analyze(structural, coupling, history)
        prediction = PredictionEngine().analyze(structural, coupling, evolution, history)

        table = Table(title="Previsão Arquitetural")
        table.add_column("Período", style="bold")
        table.add_column("Entropy", justify="right")
        table.add_column("CRI", justify="right")
        table.add_column("Confiança", justify="right")
        table.add_column("Risco")

        for p in prediction.predictions:
            table.add_row(
                f"{p.days}d",
                f"{p.predicted_entropy:.1f}",
                f"{p.predicted_cri:.1f}",
                f"{p.confidence:.0%}",
                p.risk_level,
            )

        console.print(table)
        console.print(f"\nProbabilidade de colapso (90d): {prediction.collapse_probability_90d:.0%}")


@app.command()
def version() -> None:
    """Mostra versão do AGS."""
    console.print(f"AGS v{__version__}")


if __name__ == "__main__":
    app()
