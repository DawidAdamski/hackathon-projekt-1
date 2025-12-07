#!/usr/bin/env python3
"""
Test losowej linijki z pliku.

Usage:
    uv run python tests/test_random_line.py
    uv run python tests/test_random_line.py --file ../nask_train/orig.txt
    uv run python tests/test_random_line.py --no-llm
"""

import random
import argparse
from pathlib import Path
import sys

# Dodaj parent do ścieżki
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import synthesize_line
from src.llm_client import init_llm, is_initialized


def test_random_line(
    file_path: str = "../nask_train/orig.txt",
    use_llm: bool = True,
    model: str = "ollama/PRIHLOP/PLLuM:latest",
):
    """
    Testuj losową linijkę z pliku.
    
    Args:
        file_path: Ścieżka do pliku
        use_llm: Czy używać LLM
        model: Model LLM
    """
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ Plik nie istnieje: {path}")
        return
    
    # Wczytaj linie
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total = len(lines)
    line_num = random.randint(1, total)
    line = lines[line_num - 1]
    
    print("=" * 80)
    print(f"📍 LOSOWA LINIA: {line_num}/{total}")
    print("=" * 80)
    
    # Inicjalizuj LLM
    if use_llm and not is_initialized():
        init_llm(model)
    
    # Przetwórz
    result = synthesize_line(line, use_llm=use_llm)
    
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test losowej linijki")
    parser.add_argument("--file", "-f", default="../nask_train/orig.txt", help="Plik źródłowy")
    parser.add_argument("--model", "-m", default="ollama/PRIHLOP/PLLuM:latest", help="Model LLM")
    parser.add_argument("--no-llm", action="store_true", help="Bez LLM")
    
    args = parser.parse_args()
    
    test_random_line(
        file_path=args.file,
        use_llm=not args.no_llm,
        model=args.model,
    )

