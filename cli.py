"""CLI interface for ARRS system."""
import asyncio
import typer
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path

from arrs.storage.database import Database
from arrs.storage.json_store import JSONStore
from arrs.storage.repository import Repository
from arrs.core.orchestrator import AnalysisOrchestrator
from arrs.reporting.report_generator import ReportGenerator
from config import settings

app = typer.Typer()
console = Console()


def get_repository():
    """Get initialized repository."""
    db_path = settings.database_url.replace("sqlite:///", "")
    db = Database(db_path)
    json_store = JSONStore(settings.json_storage_path)
    return Repository(db, json_store)


@app.command()
def analyze(
    url: str = typer.Argument(..., help="URL to analyze"),
    brand: str = typer.Option(None, "--brand", "-b", help="Brand name"),
    category: str = typer.Option(None, "--category", "-c", help="Product category"),
    use_case: str = typer.Option(None, "--use-case", "-u", help="Use case for simulation"),
    output: str = typer.Option(None, "--output", "-o", help="Output JSON file path")
):
    """Analyze a URL and generate ARRS score."""
    console.print(Panel.fit(
        f"[bold blue]ARRS Analysis[/bold blue]\n\nAnalyzing: {url}",
        border_style="blue"
    ))

    async def run_analysis():
        # Initialize components
        repo = get_repository()
        orchestrator = AnalysisOrchestrator(repo)

        # Run analysis
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Running analysis...", total=None)

            try:
                analysis_id = await orchestrator.analyze_url(
                    url,
                    brand=brand,
                    product_category=category,
                    use_case=use_case
                )

                progress.update(task, completed=True)

                # Get summary
                summary = await orchestrator.get_analysis_summary(analysis_id)

                # Display results
                display_results(summary)

                # Generate and save report if output specified
                if output:
                    report_gen = ReportGenerator(repo)
                    await report_gen.export_json(analysis_id, output)
                    console.print(f"\n[green]✓[/green] Report saved to: {output}")

                return analysis_id

            except Exception as e:
                console.print(f"\n[red]✗ Analysis failed:[/red] {e}")
                raise typer.Exit(code=1)

    # Run async analysis
    analysis_id = asyncio.run(run_analysis())
    console.print(f"\n[bold]Analysis ID:[/bold] {analysis_id}")


@app.command()
def report(
    analysis_id: str = typer.Argument(..., help="Analysis ID"),
    output: str = typer.Option(None, "--output", "-o", help="Output JSON file path")
):
    """Generate report for a completed analysis."""

    async def get_report():
        repo = get_repository()
        report_gen = ReportGenerator(repo)

        try:
            report_data = await report_gen.generate_report(analysis_id)

            # Display report
            display_report(report_data)

            # Save to file if requested
            if output:
                await report_gen.export_json(analysis_id, output)
                console.print(f"\n[green]✓[/green] Report saved to: {output}")

        except Exception as e:
            console.print(f"[red]✗ Error:[/red] {e}")
            raise typer.Exit(code=1)

    asyncio.run(get_report())


@app.command()
def init():
    """Initialize ARRS database."""
    console.print("[cyan]Initializing ARRS database...[/cyan]")

    async def initialize():
        db_path = settings.database_url.replace("sqlite:///", "")
        db = Database(db_path)
        await db.initialize()

    asyncio.run(initialize())
    console.print("[green]✓ Database initialized successfully![/green]")


def display_results(summary: dict):
    """Display analysis results in a formatted table."""
    console.print("\n")

    # Composite score panel
    score = summary.get("composite_score", 0)
    status = summary.get("status", "unknown")

    score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"

    console.print(Panel(
        f"[bold {score_color}]{score:.1f}/100[/bold {score_color}]",
        title="[bold]Composite ARRS Score[/bold]",
        border_style=score_color
    ))

    # Engine scores table
    table = Table(title="Engine Scores", show_header=True, header_style="bold magenta")
    table.add_column("Engine", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Weight", justify="right")
    table.add_column("Grade", justify="center")

    for engine_name, engine_data in summary.get("engine_scores", {}).items():
        score_val = engine_data["score"]
        grade_color = "green" if score_val >= 75 else "yellow" if score_val >= 50 else "red"

        table.add_row(
            engine_name,
            f"{score_val:.1f}",
            f"{engine_data['weight']:.0%}",
            f"[{grade_color}]{grade_color.upper()[0]}[/{grade_color}]"
        )

    console.print("\n", table)

    # Gaps summary
    gaps = summary.get("gaps", [])
    if gaps:
        console.print(f"\n[bold yellow]⚠ Found {len(gaps)} improvement opportunities[/bold yellow]")

        # Show top 3 critical/high gaps
        critical_gaps = [g for g in gaps if g["severity"] in ["critical", "high"]][:3]
        if critical_gaps:
            console.print("\n[bold]Top Priority Issues:[/bold]")
            for gap in critical_gaps:
                severity_color = "red" if gap["severity"] == "critical" else "yellow"
                console.print(f"  [{severity_color}]●[/{severity_color}] {gap['description']}")


def display_report(report: dict):
    """Display full report."""
    console.print("\n")

    # Header
    console.print(Panel.fit(
        f"[bold]ARRS Analysis Report[/bold]\n\n"
        f"URL: {report['url']}\n"
        f"Analysis ID: {report['analysis_id']}\n"
        f"Generated: {report['timestamp']}",
        border_style="blue"
    ))

    # Summary
    summary = report.get("summary", {})
    console.print(f"\n[bold]Composite Score:[/bold] {summary.get('composite_score', 0):.1f}/100 "
                  f"(Grade: {summary.get('grade', 'N/A')})")
    console.print(f"[bold]Interpretation:[/bold] {summary.get('interpretation', 'N/A')}")

    if summary.get("ai_citation_status") == "cited":
        console.print("\n[green]✓ Brand IS cited by AI in recommendations[/green]")
    elif summary.get("ai_citation_status") == "not_cited":
        console.print("\n[red]✗ Brand is NOT cited by AI in recommendations[/red]")

    # Recommendations
    recommendations = report.get("recommendations", [])
    if recommendations:
        console.print(f"\n[bold]Top Recommendations:[/bold]")
        for rec in recommendations[:5]:
            severity_color = "red" if rec["severity"] == "critical" else "yellow" if rec["severity"] == "high" else "blue"
            console.print(f"\n  [{severity_color}]{rec['priority']}. [{rec['severity'].upper()}][/{severity_color}]")
            console.print(f"     Issue: {rec['issue']}")
            console.print(f"     Action: {rec['action']}")


if __name__ == "__main__":
    app()
