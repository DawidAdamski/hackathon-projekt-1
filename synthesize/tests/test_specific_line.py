#!/usr/bin/env python3
"""
Test wybranej linijki z pliku.

Usage:
    uv run python tests/test_specific_line.py 21
    uv run python tests/test_specific_line.py 21 --file ../nask_train/orig.txt
    uv run python tests/test_specific_line.py 21 --no-llm
"""

import argparse
from pathlib import Path
import sys

# Dodaj parent do ścieżki
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import synthesize_line
from src.llm_client import init_llm, is_initialized


def test_specific_line(
    line_num: int,
    file_path: str = "../nask_train/orig.txt",
    use_llm: bool = True,
    model: str = "ollama/PRIHLOP/PLLuM:latest",
    verbose: bool = True,
):
    """
    Testuj wybraną linijkę z pliku.
    
    Args:
        line_num: Numer linii (1-indexed)
        file_path: Ścieżka do pliku
        use_llm: Czy używać LLM
        model: Model LLM
        verbose: Szczegółowe wyniki
    """
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ Plik nie istnieje: {path}")
        return None
    
    # Wczytaj linie
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total = len(lines)
    
    if line_num < 1 or line_num > total:
        print(f"❌ Numer linii poza zakresem (1-{total})")
        return None
    
    line = lines[line_num - 1]
    
    if verbose:
        print("=" * 80)
        print(f"📍 LINIA: {line_num}/{total}")
        print("=" * 80)
    
    # Inicjalizuj LLM
    if use_llm and not is_initialized():
        init_llm(model)
    
    # Przetwórz
    result = synthesize_line(line, use_llm=use_llm)
    
    if verbose:
        # Wyświetl wyniki
        print(f"\n📝 ORIGINAL:")
        print(f"   {result['original']}")
        
        print(f"\n🔄 AFTER FAKER:")
        print(f"   {result['after_faker']}")
        
        if result['after_fill'] and result['after_fill'] != result['after_faker']:
            print(f"\n🤖 AFTER LLM FILL:")
            print(f"   {result['after_fill']}")
        
        print(f"\n✅ FINAL:")
        print(f"   {result['final']}")
        
        print(f"\n📊 Phases: {' → '.join(result['phases_used'])}")
        
        if result['had_remaining_tokens']:
            print("⚠️  Faker nie zastąpił wszystkich tokenów")
        
        print("=" * 80)
    
    return result


# Kilka interesujących linii do testowania
INTERESTING_LINES = [
    21,  # Pierwszy "ludzki" tekst z wieloma tokenami
    22,  # Stalking case
    23,  # Problemy finansowe
    29,  # Krótka linia
    36,  # Związek
    45,  # Szkoła - bullying
]


def test_interesting_lines(
    file_path: str = "../nask_train/orig.txt",
    use_llm: bool = True,
    model: str = "ollama/PRIHLOP/PLLuM:latest",
):
    """Testuj kilka interesujących linii."""
    print("🎯 TESTOWANIE INTERESUJĄCYCH LINII")
    print("=" * 80)
    
    for line_num in INTERESTING_LINES:
        print(f"\n--- Linia {line_num} ---")
        test_specific_line(
            line_num=line_num,
            file_path=file_path,
            use_llm=use_llm,
            model=model,
            verbose=True,
        )
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test wybranej linijki")
    parser.add_argument("line", nargs="?", type=int, help="Numer linii (1-indexed)")
    parser.add_argument("--file", "-f", default="../nask_train/orig.txt", help="Plik źródłowy")
    parser.add_argument("--model", "-m", default="ollama/PRIHLOP/PLLuM:latest", help="Model LLM")
    parser.add_argument("--no-llm", action="store_true", help="Bez LLM")
    parser.add_argument("--interesting", "-i", action="store_true", help="Testuj interesujące linie")
    
    args = parser.parse_args()
    
    if args.interesting:
        test_interesting_lines(
            file_path=args.file,
            use_llm=not args.no_llm,
            model=args.model,
        )
    elif args.line:
        test_specific_line(
            line_num=args.line,
            file_path=args.file,
            use_llm=not args.no_llm,
            model=args.model,
        )
    else:
        print("Użycie: python test_specific_line.py <numer_linii>")
        print("   lub: python test_specific_line.py --interesting")

