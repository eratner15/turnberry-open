"""Click CLI for Municipal Intent Miner."""

import sys
from pathlib import Path

import click
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .database import MunicipalDatabase
from .pdf_processor import PDFProcessor
from .classifier import SignalClassifier
from .reporter import ReportGenerator

console = Console()


@click.group()
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
def cli(verbose):
    """Municipal Intent Miner - Extract procurement intelligence from municipal documents."""

    # Configure logging
    logger.remove()
    if verbose:
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.add(sys.stderr, level="INFO")


@cli.command()
@click.option('--db-path', default='./miner.db', help='Path to SQLite database')
def init(db_path):
    """Initialize the database."""

    console.print(f"[bold green]Initializing database at {db_path}[/bold green]")

    try:
        db = MunicipalDatabase(db_path)
        stats = db.get_stats()

        console.print(f"✓ Database initialized successfully")
        console.print(f"  - Documents: {stats['total_documents']}")
        console.print(f"  - Signals: {stats['total_signals']}")

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)


@cli.command()
@click.option('--pdf-dir', required=True, help='Directory containing PDFs to process')
@click.option('--vertical', required=True, help='Vertical to analyze (e.g., police-tech)')
@click.option('--db-path', default='./miner.db', help='Path to SQLite database')
@click.option('--model', default='gpt-4o-mini', help='LLM model to use')
def process(pdf_dir, vertical, db_path, model):
    """Process PDFs and extract signals."""

    pdf_dir = Path(pdf_dir)
    if not pdf_dir.exists():
        console.print(f"[bold red]Error: Directory {pdf_dir} does not exist[/bold red]")
        sys.exit(1)

    # Find all PDFs
    pdf_files = list(pdf_dir.glob('*.pdf'))
    if not pdf_files:
        console.print(f"[bold yellow]No PDF files found in {pdf_dir}[/bold yellow]")
        sys.exit(0)

    console.print(f"[bold]Found {len(pdf_files)} PDF files[/bold]")
    console.print(f"Vertical: {vertical}")
    console.print(f"Model: {model}")
    console.print("")

    # Initialize components
    db = MunicipalDatabase(db_path)
    pdf_processor = PDFProcessor()
    classifier = SignalClassifier(model_name=model)

    # Process each PDF
    processed_count = 0
    skipped_count = 0
    signals_found = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        task = progress.add_task("[cyan]Processing PDFs...", total=len(pdf_files))

        for pdf_path in pdf_files:
            progress.update(task, description=f"[cyan]Processing {pdf_path.name}...")

            # Check if already processed
            file_hash = db.calculate_file_hash(pdf_path)
            if db.document_exists(file_hash):
                logger.info(f"Skipping {pdf_path.name} (already processed)")
                skipped_count += 1
                progress.advance(task)
                continue

            try:
                # Extract text
                raw_text, metadata, page_count = pdf_processor.process_pdf(pdf_path)

                # Insert document
                document_data = {
                    'filename': metadata.filename,
                    'file_path': str(pdf_path.absolute()),
                    'file_hash': file_hash,
                    'municipality_name': metadata.municipality_name or 'Unknown',
                    'state': metadata.state,
                    'meeting_date': metadata.meeting_date,
                    'meeting_type': metadata.meeting_type,
                    'raw_text': raw_text,
                    'page_count': page_count,
                }

                doc_id = db.insert_document(document_data)

                # Classify with LLM
                llm_response = classifier.classify(
                    text=raw_text,
                    vertical=vertical,
                    metadata=metadata.dict(),
                )

                # Insert signals if found
                if llm_response.has_signal and llm_response.signals:
                    signals_data = []
                    for signal in llm_response.signals:
                        signals_data.append({
                            'municipality_name': llm_response.municipality or metadata.municipality_name or 'Unknown',
                            'state': llm_response.state or metadata.state,
                            'meeting_date': llm_response.meeting_date or metadata.meeting_date,
                            'vertical': vertical,
                            'signal_type': signal.type,
                            'specific_quote': signal.specific_quote,
                            'context': signal.context,
                            'contact_person': signal.contact_person,
                            'estimated_value': signal.estimated_value,
                            'urgency': signal.urgency,
                            'next_action': signal.next_action,
                            'confidence_score': llm_response.confidence,
                            'raw_llm_response': llm_response.json(),
                        })

                    db.insert_signals(doc_id, signals_data)
                    signals_found += len(signals_data)

                    console.print(
                        f"  [green]✓[/green] {pdf_path.name}: "
                        f"{len(signals_data)} signal(s) found "
                        f"(confidence: {llm_response.confidence:.2f})"
                    )
                else:
                    console.print(f"  [dim]○[/dim] {pdf_path.name}: No signals detected")

                # Mark as processed
                db.mark_document_processed(doc_id)
                processed_count += 1

            except Exception as e:
                console.print(f"  [red]✗[/red] {pdf_path.name}: {e}")
                logger.exception(f"Failed to process {pdf_path.name}")

            progress.advance(task)

    console.print("")
    console.print("[bold green]Processing complete![/bold green]")
    console.print(f"  - Processed: {processed_count}")
    console.print(f"  - Skipped (duplicates): {skipped_count}")
    console.print(f"  - Signals found: {signals_found}")


@cli.command()
@click.option('--db-path', default='./miner.db', help='Path to SQLite database')
@click.option('--vertical', required=True, help='Vertical to report on')
@click.option('--format', type=click.Choice(['markdown', 'csv']), default='markdown', help='Output format')
@click.option('--output', required=True, help='Output file path')
@click.option('--min-confidence', default=0.0, type=float, help='Minimum confidence score (0.0-1.0)')
def report(db_path, vertical, format, output, min_confidence):
    """Generate an intelligence report."""

    console.print(f"[bold]Generating {format} report...[/bold]")

    try:
        db = MunicipalDatabase(db_path)
        reporter = ReportGenerator(db)

        output_path = Path(output)

        if format == 'markdown':
            report_content = reporter.generate_markdown(vertical, min_confidence)
            output_path.write_text(report_content)
            console.print(f"[green]✓[/green] Markdown report written to {output_path}")
        elif format == 'csv':
            reporter.generate_csv(vertical, output_path, min_confidence)
            console.print(f"[green]✓[/green] CSV report written to {output_path}")

        # Show preview
        console.print("")
        console.print("[bold]Preview:[/bold]")
        if format == 'markdown':
            preview_lines = report_content.split('\n')[:20]
            console.print('\n'.join(preview_lines))
            if len(report_content.split('\n')) > 20:
                console.print("\n[dim]... (truncated)[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        logger.exception("Report generation failed")
        sys.exit(1)


@cli.command()
@click.option('--db-path', default='./miner.db', help='Path to SQLite database')
def stats(db_path):
    """Show database statistics."""

    try:
        db = MunicipalDatabase(db_path)
        stats = db.get_stats()

        console.print("[bold]Database Statistics:[/bold]")
        console.print(f"  Total documents: {stats['total_documents']}")
        console.print(f"  Processed documents: {stats['processed_documents']}")
        console.print(f"  Total signals: {stats['total_signals']}")

        # Signal breakdown by vertical
        signals_by_vertical = db.db.execute(
            "SELECT vertical, COUNT(*) as count FROM signals GROUP BY vertical"
        ).fetchall()

        if signals_by_vertical:
            console.print("")
            console.print("[bold]Signals by vertical:[/bold]")
            for row in signals_by_vertical:
                console.print(f"  {row['vertical']}: {row['count']}")

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)


if __name__ == '__main__':
    cli()
