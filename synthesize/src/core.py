"""
Core - główny pipeline 3-fazowy.

Flow:
    Input → Faza 1 (Faker) → Faza 2 (LLM Fill) → Faza 3 (LLM Morphology) → Output

Faza 2 jest warunkowa - wykonywana tylko gdy Faker nie zastąpił wszystkich tokenów.
"""

import json
from pathlib import Path
from typing import Optional, TypedDict
from tqdm import tqdm

from .faker_processor import process_with_faker, has_remaining_tokens
from .llm_client import (
    init_llm,
    is_initialized,
    fill_tokens,
    correct_morphology,
    fill_tokens_with_prompt,
    correct_morphology_with_prompt,
)


class SynthesisResult(TypedDict):
    """Wynik syntezy pojedynczej linii."""
    original: str
    after_faker: str
    after_fill: Optional[str]
    final: str
    phases_used: list[str]
    had_remaining_tokens: bool


def synthesize_line(
    line: str,
    use_llm: bool = True,
    use_prompt_mode: bool = False
) -> SynthesisResult:
    """
    Przetwórz pojedynczą linię przez 3-fazowy pipeline.
    
    Args:
        line: Tekst z tokenami do przetworzenia
        use_llm: Czy używać LLM (Faza 2 i 3). False = tylko Faker.
        use_prompt_mode: Użyj pełnych promptów zamiast dspy.Predict
        
    Returns:
        SynthesisResult z wynikami każdej fazy
    
    Example:
        >>> result = synthesize_line("Jestem [name] z [city].")
        >>> print(result['final'])
        "Jestem Anna z Warszawy."
    """
    result: SynthesisResult = {
        "original": line.rstrip('\n\r'),
        "after_faker": "",
        "after_fill": None,
        "final": "",
        "phases_used": [],
        "had_remaining_tokens": False,
    }
    
    # === FAZA 1: Faker ===
    text = process_with_faker(line)
    result["after_faker"] = text.rstrip('\n\r')
    result["phases_used"].append("faker")
    
    # Jeśli nie używamy LLM, kończymy tutaj
    if not use_llm:
        result["final"] = result["after_faker"]
        return result
    
    # Sprawdź czy LLM jest zainicjalizowany
    if not is_initialized():
        print("⚠️ LLM not initialized. Returning Faker-only result.")
        result["final"] = result["after_faker"]
        return result
    
    # === FAZA 2: LLM Fill (warunkowa) ===
    result["had_remaining_tokens"] = has_remaining_tokens(text)
    
    if result["had_remaining_tokens"]:
        if use_prompt_mode:
            text = fill_tokens_with_prompt(text)
        else:
            text = fill_tokens(text)
        result["after_fill"] = text.rstrip('\n\r')
        result["phases_used"].append("llm_fill")
    else:
        result["after_fill"] = result["after_faker"]
    
    # === FAZA 3: LLM Morphology ===
    if use_prompt_mode:
        text = correct_morphology_with_prompt(text)
    else:
        text = correct_morphology(text)
    result["final"] = text.rstrip('\n\r')
    result["phases_used"].append("llm_morphology")
    
    return result


def process_file(
    input_path: str | Path,
    output_path: str | Path,
    use_llm: bool = True,
    generate_jsonl: bool = True,
    use_prompt_mode: bool = False,
    llm_model: Optional[str] = None,
    use_online: bool = False,
) -> dict:
    """
    Przetwórz cały plik linia po linii.
    
    Args:
        input_path: Ścieżka do pliku wejściowego
        output_path: Ścieżka do pliku wyjściowego (.txt)
        use_llm: Czy używać LLM
        generate_jsonl: Czy generować również plik .jsonl
        use_prompt_mode: Użyj pełnych promptów zamiast dspy.Predict
        llm_model: Model LLM (jeśli None, używa domyślnego)
        
    Returns:
        Statystyki przetwarzania
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    # Sprawdź czy plik istnieje
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Utwórz katalog wyjściowy jeśli nie istnieje
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Inicjalizuj LLM jeśli potrzebny
    if use_llm and not is_initialized():
        if use_online:
            init_llm(use_online=True)
        else:
            model = llm_model or "ollama/PRIHLOP/PLLuM:latest"
            init_llm(model=model, use_online=False)
    
    # Wczytaj linie
    print(f"📂 Reading: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total_lines = len(lines)
    print(f"📊 Total lines: {total_lines}")
    
    # Statystyki
    stats = {
        "total_lines": total_lines,
        "processed": 0,
        "with_tokens": 0,
        "with_remaining_tokens": 0,
        "errors": 0,
    }
    
    # Otwórz pliki wyjściowe na początku (zapis na bieżąco)
    print(f"💾 Opening output files for streaming write...")
    txt_file = open(output_path, 'w', encoding='utf-8', buffering=1)  # Line buffering
    
    jsonl_file = None
    if generate_jsonl:
        jsonl_path = output_path.with_suffix('.jsonl')
        jsonl_file = open(jsonl_path, 'w', encoding='utf-8', buffering=1)  # Line buffering
    
    line_number = 0
    
    try:
        # Przetwarzaj z progress barem i zapisuj na bieżąco
        for line in tqdm(lines, desc="Synthesizing", unit="lines"):
            line_number += 1
            try:
                result = synthesize_line(line, use_llm=use_llm, use_prompt_mode=use_prompt_mode)
                stats["processed"] += 1
                
                if result["had_remaining_tokens"]:
                    stats["with_remaining_tokens"] += 1
                if result["original"] != result["after_faker"]:
                    stats["with_tokens"] += 1
                
                # Zapisuj natychmiast po przetworzeniu
                txt_file.write(result["final"] + '\n')
                txt_file.flush()  # Wymuś zapis do pliku
                
                if jsonl_file:
                    obj = {
                        "line": line_number,
                        "original": result["original"],
                        "synthetic": result["final"],
                        "phases": result["phases_used"],  # Dla debugowania - które fazy zostały użyte
                    }
                    jsonl_file.write(json.dumps(obj, ensure_ascii=False) + '\n')
                    jsonl_file.flush()  # Wymuś zapis do pliku
                    
            except Exception as e:
                print(f"\n⚠️ Error processing line {line_number}: {e}")
                stats["errors"] += 1
                # Zapisz oryginalną linię jako fallback
                error_result = line.rstrip('\n\r')
                txt_file.write(error_result + '\n')
                txt_file.flush()
                
                if jsonl_file:
                    obj = {
                        "line": line_number,
                        "original": error_result,
                        "synthetic": error_result,
                        "phases": ["error"],  # Dla debugowania - oznaczenie błędu
                    }
                    jsonl_file.write(json.dumps(obj, ensure_ascii=False) + '\n')
                    jsonl_file.flush()
    
    finally:
        # Zamknij pliki
        txt_file.close()
        if jsonl_file:
            jsonl_file.close()
        
        print(f"\n💾 Files saved: {output_path}")
        if generate_jsonl:
            print(f"💾 Files saved: {output_path.with_suffix('.jsonl')}")
    
    # Podsumowanie
    print(f"\n✅ Done!")
    print(f"   Total lines: {stats['total_lines']}")
    print(f"   Processed: {stats['processed']}")
    print(f"   With tokens: {stats['with_tokens']}")
    print(f"   Required LLM fill: {stats['with_remaining_tokens']}")
    if stats['errors'] > 0:
        print(f"   ⚠️ Errors: {stats['errors']}")
    
    return stats


def synthesize_batch(
    lines: list[str],
    use_llm: bool = True,
    use_prompt_mode: bool = False,
    show_progress: bool = True,
) -> list[SynthesisResult]:
    """
    Przetwórz batch linii (dla REST API).
    
    Args:
        lines: Lista linii do przetworzenia
        use_llm: Czy używać LLM
        use_prompt_mode: Użyj pełnych promptów
        show_progress: Pokaż progress bar
        
    Returns:
        Lista wyników
    """
    results = []
    iterator = tqdm(lines, desc="Processing", unit="lines") if show_progress else lines
    
    for line in iterator:
        result = synthesize_line(line, use_llm=use_llm, use_prompt_mode=use_prompt_mode)
        results.append(result)
    
    return results

