#!/usr/bin/env python3
"""
Test N losowych linijek z pliku.

Usage:
    uv run python tests/test_n_lines.py 5
    uv run python tests/test_n_lines.py 10 --file ../nask_train/orig.txt
    uv run python tests/test_n_lines.py 5 --no-llm
"""

import random
import argparse
from pathlib import Path
import sys

# Dodaj parent do ścieżki
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import synthesize_line
from src.llm_client import init_llm, is_initialized
from src.faker_processor import has_remaining_tokens


def test_n_lines(
    n: int,
    file_path: str = "../nask_train/orig.txt",
    use_llm: bool = True,
    model: str = "ollama/PRIHLOP/PLLuM:latest",
    compact: bool = False,
):
    """
    Testuj N losowych linijek z pliku.
    
    Args:
        n: Liczba linijek do testowania
        file_path: Ścieżka do pliku
        use_llm: Czy używać LLM
        model: Model LLM
        compact: Kompaktowy output (tylko podsumowanie)
    """
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ Plik nie istnieje: {path}")
        return
    
    # Wczytaj linie
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total = len(lines)
    n = min(n, total)
    
    # Losuj indeksy
    indices = random.sample(range(total), n)
    indices.sort()
    
    print("=" * 80)
    print(f"🎲 TESTOWANIE {n} LOSOWYCH LINII z {total}")
    print(f"📂 Plik: {path}")
    print(f"🤖 LLM: {'Tak' if use_llm else 'Nie'}")
    print("=" * 80)
    
    # Inicjalizuj LLM
    if use_llm and not is_initialized():
        init_llm(model)
    
    # Statystyki
    stats = {
        "total": n,
        "with_tokens": 0,
        "with_remaining_tokens": 0,
        "phases": {},
    }
    
    results = []
    
    for i, idx in enumerate(indices, 1):
        line_num = idx + 1
        line = lines[idx]
        
        # Przetwórz
        result = synthesize_line(line, use_llm=use_llm)
        results.append((line_num, result))
        
        # Statystyki
        if result['original'] != result['after_faker']:
            stats['with_tokens'] += 1
        
        if result['had_remaining_tokens']:
            stats['with_remaining_tokens'] += 1
        
        for phase in result['phases_used']:
            stats['phases'][phase] = stats['phases'].get(phase, 0) + 1
        
        if not compact:
            print(f"\n[{i}/{n}] Linia {line_num}")
            print(f"   📝 ORIG:  {result['original'][:100]}{'...' if len(result['original']) > 100 else ''}")
            print(f"   ✅ FINAL: {result['final'][:100]}{'...' if len(result['final']) > 100 else ''}")
            print(f"   📊 Phases: {' → '.join(result['phases_used'])}")
    
    # Podsumowanie
    print("\n" + "=" * 80)
    print("📊 PODSUMOWANIE")
    print("=" * 80)
    print(f"   Przetworzone: {stats['total']}")
    print(f"   Z tokenami: {stats['with_tokens']}")
    print(f"   Wymagające LLM fill: {stats['with_remaining_tokens']}")
    print(f"\n   Fazy użyte:")
    for phase, count in sorted(stats['phases'].items()):
        print(f"      • {phase}: {count}")
    
    # Przykłady (jeśli compact)
    if compact and results:
        print("\n📝 PRZYKŁADY (pierwsze 3):")
        for line_num, result in results[:3]:
            print(f"\n   Linia {line_num}:")
            print(f"   ORIG:  {result['original'][:80]}...")
            print(f"   FINAL: {result['final'][:80]}...")
    
    print("=" * 80)
    
    return stats


def compare_modes(
    n: int = 5,
    file_path: str = "../nask_train/orig.txt",
    model: str = "ollama/PRIHLOP/PLLuM:latest",
):
    """
    Porównaj wyniki z LLM i bez LLM.
    """
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ Plik nie istnieje: {path}")
        return
    
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total = len(lines)
    n = min(n, total)
    indices = random.sample(range(total), n)
    indices.sort()
    
    print("=" * 80)
    print(f"⚖️ PORÓWNANIE: FAKER vs LLM ({n} linii)")
    print("=" * 80)
    
    # Inicjalizuj LLM
    if not is_initialized():
        init_llm(model)
    
    for idx in indices:
        line_num = idx + 1
        line = lines[idx]
        
        # Tylko Faker
        result_faker = synthesize_line(line, use_llm=False)
        
        # Z LLM
        result_llm = synthesize_line(line, use_llm=True)
        
        print(f"\n📍 Linia {line_num}")
        print(f"   📝 ORIGINAL:    {result_faker['original'][:70]}...")
        print(f"   🔄 FAKER ONLY:  {result_faker['final'][:70]}...")
        print(f"   🤖 WITH LLM:    {result_llm['final'][:70]}...")
        
        # Różnica?
        if result_faker['final'] != result_llm['final']:
            print(f"   ✨ RÓŻNICA: LLM poprawił tekst")
        else:
            print(f"   ⚖️ IDENTYCZNE")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test N losowych linijek")
    parser.add_argument("n", nargs="?", type=int, default=5, help="Liczba linijek")
    parser.add_argument("--file", "-f", default="../nask_train/orig.txt", help="Plik źródłowy")
    parser.add_argument("--model", "-m", default="ollama/PRIHLOP/PLLuM:latest", help="Model LLM")
    parser.add_argument("--no-llm", action="store_true", help="Bez LLM")
    parser.add_argument("--compact", "-c", action="store_true", help="Kompaktowy output")
    parser.add_argument("--compare", action="store_true", help="Porównaj Faker vs LLM")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_modes(
            n=args.n,
            file_path=args.file,
            model=args.model,
        )
    else:
        test_n_lines(
            n=args.n,
            file_path=args.file,
            use_llm=not args.no_llm,
            model=args.model,
            compact=args.compact,
        )

