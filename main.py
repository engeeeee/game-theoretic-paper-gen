"""
Game-Theoretic Multi-Agent System

Command-line interface for academic verification through adversarial debate.
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.proponent import ProponentAgent
from src.agents.reviewer import ReviewerAgent
from src.agents.base_agent import LLMProvider
from src.engine.adaptive_debate import AdaptiveDebateEngine
from src.output.consensus import ConsensusGenerator
from src.output.report import ReportGenerator
from src.output.paper_generator import PaperGenerator
from src.input.requirements_parser import RequirementsParser
from src.input.intelligent_analyzer import IntelligentAnalyzer

console = Console()


def print_header():
    """Print application header."""
    console.print(Panel.fit(
        "[bold blue]Game-Theoretic Multi-Agent System[/bold blue]\n"
        "[dim]Academic Verification through Adversarial Debate[/dim]",
        border_style="blue"
    ))


def check_api_keys():
    """Check if required API keys are configured."""
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    if not openai_key and not google_key:
        console.print("[red]Error: No API keys configured.[/red]")
        console.print("Please set OPENAI_API_KEY or GOOGLE_API_KEY in .env file")
        console.print("\nCopy .env.example to .env and add your keys:")
        console.print("  cp .env.example .env")
        return False
    
    provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    if provider == "openai" and not openai_key:
        console.print("[yellow]Warning: OpenAI selected but no key found. Trying Google.[/yellow]")
        os.environ["DEFAULT_LLM_PROVIDER"] = "google"
    elif provider == "google" and not google_key:
        console.print("[yellow]Warning: Google selected but no key found. Trying OpenAI.[/yellow]")
        os.environ["DEFAULT_LLM_PROVIDER"] = "openai"
    
    return True


@click.group()
def cli():
    """Game-Theoretic Multi-Agent Academic Verification System."""
    pass


@cli.command()
@click.argument('question')
@click.option('--context', '-c', help='Additional context or paper content')
@click.option('--context-file', '-f', type=click.Path(exists=True), help='File with context')
@click.option('--max-rounds', '-r', default=None, type=int, help='Maximum debate rounds')
@click.option('--strictness', '-s', default='high', type=click.Choice(['low', 'medium', 'high']))
@click.option('--output', '-o', default=None, help='Output file for report')
@click.option('--paper', is_flag=True, help='Generate exportable academic paper')
@click.option('--provider', '-p', default=None, type=click.Choice(['openai', 'google']))
def verify(question, context, context_file, max_rounds, strictness, output, paper, provider):
    """
    Verify a claim or question through adversarial debate.
    
    Example:
        python main.py verify "Is the methodology in paper X reliable?"
    """
    print_header()
    
    if not check_api_keys():
        return
    
    # Load context from file if provided
    if context_file:
        with open(context_file, 'r', encoding='utf-8') as f:
            context = f.read()
    
    # Set provider if specified
    if provider:
        os.environ["DEFAULT_LLM_PROVIDER"] = provider
    
    console.print(f"\n[bold]Question:[/bold] {question}")
    if context:
        console.print(f"[dim]Context provided: {len(context)} characters[/dim]")
    
    # Run the verification
    asyncio.run(run_verification(
        question=question,
        context=context,
        max_rounds=max_rounds,
        strictness=strictness,
        output_file=output,
        generate_paper=paper
    ))


async def run_verification(
    question: str,
    context: str = None,
    max_rounds: int = None,
    strictness: str = "high",
    output_file: str = None,
    generate_paper: bool = False
):
    """Run the full verification process."""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Initialize agents
        task = progress.add_task("Initializing agents...", total=None)
        
        provider = LLMProvider(os.getenv("DEFAULT_LLM_PROVIDER", "openai"))
        
        proponent = ProponentAgent(provider=provider)
        reviewer = ReviewerAgent(provider=provider, strictness=strictness)
        
        progress.update(task, description="Agents initialized")
        
        # Initialize debate engine
        progress.update(task, description="Setting up debate engine...")
        
        engine = AdaptiveDebateEngine(
            proponent=proponent,
            reviewer=reviewer,
            max_rounds=max_rounds
        )
        
        # Run debate
        progress.update(task, description="Running adversarial debate...")
        
        try:
            result = await engine.run_debate(question, context)
        except Exception as e:
            console.print(f"[red]Error during debate: {e}[/red]")
            return
        
        progress.update(task, description="Generating consensus...")
        
        # Generate consensus
        consensus_gen = ConsensusGenerator()
        consensus = consensus_gen.generate(result, result.voting_result)
        
        progress.update(task, description="Creating report...")
        
        # Generate report
        report_gen = ReportGenerator()
        report = report_gen.generate_full_report(
            debate_result=result,
            consensus=consensus,
            voting_result=result.voting_result
        )
    
    # Display results
    console.print("\n")
    display_results(result, consensus)
    
    # Save report if output file specified
    if output_file:
        report_gen.save_report(report, output_file)
        console.print(f"\n[green]Report saved to: {output_file}[/green]")
    else:
        # Generate default output file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_output = f"verification_report_{timestamp}.txt"
        report_gen.save_report(report, default_output)
        console.print(f"\n[green]Report saved to: {default_output}[/green]")
    
    # Generate academic paper if requested
    if generate_paper:
        console.print("\n[bold blue]Generating Academic Paper...[/bold blue]")
        paper_gen = PaperGenerator()
        paper = paper_gen.generate_paper(question, result, consensus, result.voting_result)
        exports = paper_gen.export_to_formats(paper)
        
        console.print(Panel(
            f"[green]Paper exported to:[/green]\n"
            f"  Markdown: {exports['markdown']}\n"
            f"  Text: {exports['text']}",
            title="PAPER OUTPUT",
            border_style="green"
        ))
        console.print("\n[bold green]Paper content ready for use in your thesis![/bold green]")


def display_results(result, consensus):
    """Display verification results."""
    
    # Verdict panel
    verdict_color = {
        "VALIDATED": "green",
        "PARTIALLY VALIDATED": "yellow",
        "REJECTED": "red",
        "INCONCLUSIVE": "dim",
    }.get(consensus.verdict, "white")
    
    console.print(Panel(
        f"[bold {verdict_color}]{consensus.verdict}[/bold {verdict_color}]\n"
        f"Confidence: {consensus.confidence:.1f}%",
        title="VERDICT",
        border_style=verdict_color
    ))
    
    # Scoring table
    if result.voting_result:
        table = Table(title="Scoring Breakdown")
        table.add_column("Criterion", style="cyan")
        table.add_column("Score", justify="right")
        table.add_column("Status", justify="center")
        
        for criterion, score in result.voting_result.criterion_scores.items():
            status = "[green]PASS[/green]" if score >= 75 else "[red]FAIL[/red]"
            table.add_row(criterion.capitalize(), f"{score:.1f}", status)
        
        table.add_row(
            "[bold]WEIGHTED AVG[/bold]",
            f"[bold]{result.voting_result.weighted_average:.1f}[/bold]",
            "[bold green]PASS[/bold green]" if result.voting_result.passed else "[bold red]FAIL[/bold red]"
        )
        
        console.print(table)
    
    # Statistics
    stats_table = Table(title="Debate Statistics")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", justify="right")
    
    stats_table.add_row("Total Rounds", str(result.total_rounds))
    stats_table.add_row("Re-evaluations", str(result.re_evaluations))
    stats_table.add_row("Status", result.status.value)
    stats_table.add_row("Verified Claims", str(len(consensus.verified_claims)))
    stats_table.add_row("Rejected Claims", str(len(consensus.rejected_claims)))
    
    console.print(stats_table)


@cli.command()
def config():
    """Show current configuration."""
    print_header()
    
    table = Table(title="Current Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value")
    
    config_items = [
        ("LLM Provider", os.getenv("DEFAULT_LLM_PROVIDER", "openai")),
        ("OpenAI Model", os.getenv("OPENAI_MODEL", "gpt-4o")),
        ("Google Model", os.getenv("GOOGLE_MODEL", "gemini-pro")),
        ("Max Rounds", os.getenv("MAX_DEBATE_ROUNDS", "20")),
        ("Quality Threshold", os.getenv("QUALITY_THRESHOLD", "85")),
        ("Voting Threshold", os.getenv("VOTING_PASS_THRESHOLD", "75")),
        ("Max Retries", os.getenv("MAX_RETRIES", "3")),
        ("OpenAI Key", "***" if os.getenv("OPENAI_API_KEY") else "[red]Not set[/red]"),
        ("Google Key", "***" if os.getenv("GOOGLE_API_KEY") else "[red]Not set[/red]"),
    ]
    
    for setting, value in config_items:
        table.add_row(setting, str(value))
    
    console.print(table)


@cli.command()
@click.argument('text')
def check_citations(text):
    """Check citations in text without full debate."""
    print_header()
    
    from src.citation_moat.moat_engine import CitationMoatEngine
    
    console.print("[bold]Checking citations...[/bold]\n")
    
    engine = CitationMoatEngine(strict_mode=True)
    
    async def run_check():
        return await engine.verify_text(text)
    
    report = asyncio.run(run_check())
    
    console.print(engine.generate_report_text(report))


@cli.command()
@click.argument('requirements', required=False)
@click.option('--requirements-file', '-f', type=click.Path(exists=True), help='File with paper requirements')
@click.option('--output-dir', '-o', default='output', help='Output directory for generated paper')
@click.option('--provider', '-p', default=None, type=click.Choice(['openai', 'google']))
def write(requirements, requirements_file, output_dir, provider):
    """
    Write a paper based on detailed requirements.
    
    Understands complex paper requirements including:
    - Word count, page count
    - Citation style (APA, MLA, Chicago, etc.)
    - Required sections
    - Methodology type
    - Source requirements
    
    Examples:
        python main.py write "Write a 3000-word essay on climate change using APA"
        python main.py write -f requirements.txt
    """
    print_header()
    
    if not check_api_keys():
        return
    
    # Load requirements
    if requirements_file:
        with open(requirements_file, 'r', encoding='utf-8') as f:
            requirements = f.read()
    
    if not requirements:
        console.print("[red]Error: Please provide requirements or a requirements file[/red]")
        return
    
    # Set provider if specified
    if provider:
        os.environ["DEFAULT_LLM_PROVIDER"] = provider
    
    # Parse requirements
    parser = RequirementsParser()
    req = parser.parse(requirements)
    
    # Display parsed requirements
    console.print("\n[bold cyan]Parsed Requirements:[/bold cyan]")
    console.print(parser.format_requirements(req))
    
    # Convert to agent prompt
    agent_prompt = parser.to_agent_prompt(req)
    
    console.print(f"\n[bold]Topic:[/bold] {req.topic}")
    console.print(f"[bold]Format:[/bold] {req.format_type}")
    console.print(f"[bold]Citation Style:[/bold] {req.citation_style}")
    
    # Run verification with enhanced context
    asyncio.run(run_verification(
        question=agent_prompt,
        context=requirements,
        max_rounds=None,
        strictness="high",
        output_file=None,
        generate_paper=True  # Always generate paper for write command
    ))


@cli.command()
@click.argument('input_text', required=False)
@click.option('--input-file', '-f', type=click.Path(exists=True), help='File with paper requirements')
@click.option('--provider', '-p', default=None, type=click.Choice(['openai', 'google']))
def smart(input_text, input_file, provider):
    """
    Intelligently understand ANY format of paper requirements.
    
    Uses LLM to adaptively parse requirements - no templates needed.
    Can understand:
    - Casual conversations
    - Assignment briefs
    - Mixed language
    - Incomplete specifications
    
    Examples:
        python main.py smart "我需要一篇关于AI的论文，大概5000字，要有文献综述"
        python main.py smart "Write something about climate change, maybe 10 pages, APA format"
        python main.py smart -f my_assignment.txt
    """
    print_header()
    
    if not check_api_keys():
        return
    
    # Load input
    if input_file:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_text = f.read()
    
    if not input_text:
        console.print("[red]Error: Please provide input or an input file[/red]")
        return
    
    # Set provider if specified
    if provider:
        os.environ["DEFAULT_LLM_PROVIDER"] = provider
    
    console.print("\n[bold cyan]Intelligently analyzing your requirements...[/bold cyan]")
    
    # Use intelligent analyzer
    analyzer = IntelligentAnalyzer()
    
    async def analyze_requirements():
        return await analyzer.analyze(input_text)
    
    req = asyncio.run(analyze_requirements())
    
    # Display parsed requirements
    console.print(f"\n{analyzer.format_for_display(req)}")
    
    # Check if clarification needed
    if req.unclear_aspects:
        console.print("\n[yellow]Some aspects may need clarification (see above)[/yellow]")
    
    # Convert to agent prompt
    agent_prompt = analyzer.to_agent_prompt(req)
    
    console.print(f"\n[bold green]Proceeding with parsed requirements...[/bold green]")
    
    # Run verification with intelligent requirements
    asyncio.run(run_verification(
        question=agent_prompt,
        context=input_text,
        max_rounds=None,
        strictness="high",
        output_file=None,
        generate_paper=True
    ))


if __name__ == "__main__":
    cli()
