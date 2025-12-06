#!/usr/bin/env python3
"""
Synthesize - CLI i REST API dla syntezy danych PII.

Usage:
    # Przetwórz plik
    uv run python main.py process ../nask_train/orig.txt -o output.txt
    
    # Testuj losową linijkę
    uv run python main.py test --random
    
    # Testuj konkretną linijkę
    uv run python main.py test --line 21
    
    # Testuj N losowych linijek
    uv run python main.py test --random-n 5
    
    # Uruchom REST API
    uv run python main.py serve --port 8000
"""

import random
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.core import synthesize_line, process_file, synthesize_batch
from src.llm_client import init_llm, is_initialized
from src.faker_processor import get_supported_tokens

# CLI App
app = typer.Typer(
    name="synthesize",
    help="Moduł do syntezy danych PII w języku polskim",
    add_completion=False,
)

console = Console()

# Domyślna ścieżka do pliku
DEFAULT_INPUT = "../nask_train/orig.txt"
DEFAULT_MODEL = "ollama/PRIHLOP/PLLuM:latest"


@app.command()
def process(
    input_file: str = typer.Argument(DEFAULT_INPUT, help="Plik wejściowy z tokenami"),
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Plik wyjściowy"),
    model: str = typer.Option(DEFAULT_MODEL, "-m", "--model", help="Model LLM"),
    no_llm: bool = typer.Option(False, "--no-llm", help="Tylko Faker (bez LLM)"),
    no_jsonl: bool = typer.Option(False, "--no-jsonl", help="Nie generuj pliku .jsonl"),
    prompt_mode: bool = typer.Option(False, "--prompt-mode", help="Użyj pełnych promptów"),
):
    """
    Przetwórz plik z tokenami i wygeneruj dane syntetyczne.
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        console.print(f"[red]✗ Plik nie istnieje: {input_path}[/red]")
        raise typer.Exit(1)
    
    # Ustal ścieżkę wyjściową
    if output:
        output_path = Path(output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_synthetic.txt"
    
    console.print(f"[blue]📂 Input:[/blue] {input_path}")
    console.print(f"[blue]📂 Output:[/blue] {output_path}")
    console.print(f"[blue]🤖 Model:[/blue] {model if not no_llm else 'DISABLED'}")
    console.print()
    
    # Przetwórz
    stats = process_file(
        input_path=input_path,
        output_path=output_path,
        use_llm=not no_llm,
        generate_jsonl=not no_jsonl,
        use_prompt_mode=prompt_mode,
        llm_model=model,
    )
    
    console.print(f"\n[green]✅ Zakończono pomyślnie![/green]")


@app.command()
def test(
    input_file: str = typer.Option(DEFAULT_INPUT, "-f", "--file", help="Plik źródłowy"),
    line: Optional[int] = typer.Option(None, "-l", "--line", help="Numer linii do testowania"),
    random_line: bool = typer.Option(False, "-r", "--random", help="Losowa linijka"),
    random_n: Optional[int] = typer.Option(None, "-n", "--random-n", help="N losowych linijek"),
    model: str = typer.Option(DEFAULT_MODEL, "-m", "--model", help="Model LLM"),
    no_llm: bool = typer.Option(False, "--no-llm", help="Tylko Faker (bez LLM)"),
    prompt_mode: bool = typer.Option(False, "--prompt-mode", help="Użyj pełnych promptów"),
):
    """
    Testuj pojedyncze linijki z pliku.
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        console.print(f"[red]✗ Plik nie istnieje: {input_path}[/red]")
        raise typer.Exit(1)
    
    # Wczytaj plik
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total_lines = len(lines)
    console.print(f"[blue]📂 Plik:[/blue] {input_path} ({total_lines} linii)")
    console.print()
    
    # Inicjalizuj LLM jeśli potrzebny
    if not no_llm:
        if not is_initialized():
            init_llm(model)
    
    # Wybierz linijki do testowania
    if line is not None:
        if line < 1 or line > total_lines:
            console.print(f"[red]✗ Numer linii poza zakresem (1-{total_lines})[/red]")
            raise typer.Exit(1)
        test_indices = [line - 1]
    elif random_line:
        test_indices = [random.randint(0, total_lines - 1)]
    elif random_n:
        n = min(random_n, total_lines)
        test_indices = random.sample(range(total_lines), n)
    else:
        console.print("[yellow]Użyj --line, --random lub --random-n[/yellow]")
        raise typer.Exit(1)
    
    # Testuj każdą linijkę
    for idx in test_indices:
        line_text = lines[idx]
        line_num = idx + 1
        
        console.print(Panel(f"[bold]Linia {line_num}/{total_lines}[/bold]", style="blue"))
        
        # Przetwórz
        result = synthesize_line(
            line_text,
            use_llm=not no_llm,
            use_prompt_mode=prompt_mode,
        )
        
        # Wyświetl wyniki
        # Rich interpretuje [text] jako markdown link, więc escape'ujemy nawiasy
        from rich.markup import escape
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Faza", style="dim", width=15)
        table.add_column("Tekst", no_wrap=False)
        
        # escape() zamienia [ na [[ aby Rich nie interpretował jako markdown
        table.add_row("📝 ORIGINAL", escape(result["original"]))
        table.add_row("🔄 AFTER FAKER", escape(result["after_faker"]))
        
        if result["after_fill"] and result["after_fill"] != result["after_faker"]:
            table.add_row("🤖 AFTER LLM FILL", escape(result["after_fill"]))
        
        table.add_row("✅ FINAL", escape(result["final"]))
        
        console.print(table)
        
        # Info o fazach
        phases_str = " → ".join(result["phases_used"])
        console.print(f"[dim]Phases: {phases_str}[/dim]")
        
        if result["had_remaining_tokens"]:
            console.print("[yellow]⚠️ Faker nie zastąpił wszystkich tokenów - LLM pomógł[/yellow]")
        
        console.print()


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", help="Host"),
    port: int = typer.Option(8000, "-p", "--port", help="Port"),
    model: str = typer.Option(DEFAULT_MODEL, "-m", "--model", help="Model LLM"),
):
    """
    Uruchom REST API server.
    """
    import uvicorn
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    
    # Inicjalizuj LLM
    init_llm(model)
    
    # FastAPI app
    api = FastAPI(
        title="Synthesize API",
        description="API do syntezy danych PII w języku polskim",
        version="0.1.0",
    )
    
    class SynthesizeRequest(BaseModel):
        text: str
        use_llm: bool = True
        use_prompt_mode: bool = False
    
    class SynthesizeBatchRequest(BaseModel):
        lines: list[str]
        use_llm: bool = True
        use_prompt_mode: bool = False
    
    class SynthesizeResponse(BaseModel):
        original: str
        synthetic: str
        phases_used: list[str]
    
    @api.post("/synthesize", response_model=SynthesizeResponse)
    async def synthesize_endpoint(request: SynthesizeRequest):
        """Syntetyzuj pojedynczy tekst."""
        result = synthesize_line(
            request.text,
            use_llm=request.use_llm,
            use_prompt_mode=request.use_prompt_mode,
        )
        return SynthesizeResponse(
            original=result["original"],
            synthetic=result["final"],
            phases_used=result["phases_used"],
        )
    
    @api.post("/synthesize/batch")
    async def synthesize_batch_endpoint(request: SynthesizeBatchRequest):
        """Syntetyzuj batch tekstów."""
        results = synthesize_batch(
            request.lines,
            use_llm=request.use_llm,
            use_prompt_mode=request.use_prompt_mode,
            show_progress=False,
        )
        return [
            {
                "original": r["original"],
                "synthetic": r["final"],
                "phases_used": r["phases_used"],
            }
            for r in results
        ]
    
    @api.get("/health")
    async def health():
        """Health check."""
        return {"status": "ok", "llm_initialized": is_initialized()}
    
    @api.get("/tokens")
    async def tokens():
        """Lista obsługiwanych tokenów."""
        return {"tokens": get_supported_tokens()}
    
    console.print(f"[green]🚀 Starting server on http://{host}:{port}[/green]")
    console.print(f"[dim]📖 Docs: http://{host}:{port}/docs[/dim]")
    
    uvicorn.run(api, host=host, port=port)


@app.command()
def tokens():
    """
    Pokaż listę obsługiwanych tokenów.
    """
    supported = get_supported_tokens()
    
    console.print("[bold]Obsługiwane tokeny:[/bold]\n")
    
    for token in sorted(supported):
        console.print(f"  • [{token}]")
    
    console.print(f"\n[dim]Łącznie: {len(supported)} tokenów[/dim]")


if __name__ == "__main__":
    app()

