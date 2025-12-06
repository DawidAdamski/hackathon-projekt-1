# Synthesize - Architektura Modułu

## 📋 Cel

Prosty, efektywny moduł do syntezy danych PII w języku polskim. Zastępuje tokeny `[name]`, `[city]`, etc. w tekście syntetycznymi danymi z zachowaniem poprawnej morfologii.

**Kluczowe cechy:**
- ✅ 3-fazowy pipeline (Faker → LLM Fill → LLM Morphology)
- ✅ Zapis na bieżąco (streaming) - wyniki widoczne natychmiast
- ✅ Optymalizacja TEKST_JEST_TAKI_SAM - oszczędność tokenów
- ✅ Obsługa wszystkich tokenów z dokumentacji DANE_BEZ_TWARZY.md
- ✅ Prosta konfiguracja DSPy (wzorzec z TestDspy)
- ✅ REST API + CLI

**Kluczowe cechy:**
- ✅ 3-fazowy pipeline (Faker → LLM Fill → LLM Morphology)
- ✅ Zapis na bieżąco (streaming) - wyniki widoczne natychmiast
- ✅ Optymalizacja TEKST_JEST_TAKI_SAM - oszczędność tokenów
- ✅ Obsługa wszystkich tokenów z dokumentacji DANE_BEZ_TWARZY.md
- ✅ Prosta konfiguracja DSPy (wzorzec z TestDspy)
- ✅ REST API + CLI

---

## 🔄 Flow Danych

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INPUT                                          │
│                     Plik .txt LUB REST API                                  │
│           (linia = tekst z tokenami [name], [city], etc.)                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FAZA 1: FAKER                                     │
│   • Regex znajduje wszystkie tokeny [...]                                   │
│   • Faker (pl_PL) podstawia syntetyczne dane                                │
│   • Szybkie, deterministyczne                                               │
│   • Output: tekst z większością tokenów zastąpionych                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FAZA 2: GREP + LLM FILL                                │
│   • Regex sprawdza: czy są jeszcze tokeny [...]?                            │
│   • Jeśli TAK → LLM uzupełnia brakujące tokeny                              │
│   • Jeśli NIE → pomiń (optymalizacja!)                                      │
│   • Output: tekst bez żadnych tokenów [...]                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FAZA 3: LLM MORPHOLOGY                                   │
│   • LLM sprawdza morfologię całego zdania                                   │
│   • Poprawia formy gramatyczne (przypadki, rodzaj, etc.)                    │
│   • Jeśli "Róża prosił" → "Róża prosiła"                                    │
│   • Output: poprawny gramatycznie tekst                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              OUTPUT                                         │
│                   Pliki: output.txt + output.jsonl                          │
│   (JSONL: {"line": N, "original": "...", "synthetic": "...", "phases": [...]}) │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Struktura Projektu

```
synthesize/
├── pyproject.toml          # uv + Python 3.12
├── ARCHITECTURE.md         # Ten dokument
│
├── src/
│   ├── __init__.py
│   ├── core.py             # Główny pipeline 3-fazowy
│   ├── faker_processor.py  # Faza 1: Faker
│   ├── llm_client.py       # DSPy wrapper (jak TestDspy)
│   └── prompts.py          # Prompty dla LLM
│
├── main.py                 # CLI + REST API (FastAPI)
│
└── tests/
    ├── __init__.py
    ├── test_random_line.py     # Testuj losową linijkę
    ├── test_specific_line.py   # Testuj wybraną linijkę
    └── test_n_lines.py         # Testuj N losowych linijek
```

---

## 🧩 Komponenty

### 1. `llm_client.py` - Prosty DSPy Wrapper

```python
# Wzorzec z TestDspy - PROSTO!
import dspy

def init_llm(model: str = "ollama/PRIHLOP/PLLuM:latest"):
    """Inicjalizacja LLM - jedna linia jak w TestDspy."""
    lm = dspy.LM(model=model)
    dspy.configure(lm=lm)
    return lm

# Signature dla uzupełniania tokenów
class FillTokensSignature(dspy.Signature):
    """Uzupełnij brakujące tokeny [...] w tekście."""
    text: str = dspy.InputField(desc="Tekst z tokenami do uzupełnienia")
    filled: str = dspy.OutputField(desc="Tekst z uzupełnionymi tokenami")

# Signature dla korekty morfologii
class CorrectMorphologySignature(dspy.Signature):
    """Popraw morfologię tekstu (przypadki, formy czasowników)."""
    text: str = dspy.InputField(desc="Tekst do korekty")
    corrected: str = dspy.OutputField(desc="Tekst z poprawioną morfologią")

# Funkcje główne
def fill_tokens(text: str) -> str:
    """Faza 2: Uzupełnij brakujące tokeny używając dspy.Predict."""
    module = dspy.Predict(FillTokensSignature)
    result = module(text=text)
    return _clean_response(result.filled)  # Czyszczenie odpowiedzi LLM

def correct_morphology(text: str) -> str:
    """Faza 3: Popraw morfologię używając dspy.Predict."""
    module = dspy.Predict(CorrectMorphologySignature)
    result = module(text=text)
    cleaned = _clean_response(result.corrected)
    
    # OPTYMALIZACJA: Obsługa TEKST_JEST_TAKI_SAM
    if cleaned.strip().upper() == "TEKST_JEST_TAKI_SAM":
        return text  # Zwróć oryginalny tekst
    
    return cleaned

# Alternatywne funkcje z pełnymi promptami (fallback)
def fill_tokens_with_prompt(text: str) -> str:
    """Alternatywa używająca pełnych promptów zamiast dspy.Predict."""
    # Używa bezpośrednio _lm() z pełnym promptem
    
def _clean_response(response: str) -> str:
    """Czyści odpowiedź LLM z formatów JSON, markdown, prefiksów."""
    # Usuwa: {corrected: "..."}, [{'text': '...'}], ```, "Oto poprawiony tekst:", etc.
    # ZACHOWUJE wulgaryzmy
```

### 2. `faker_processor.py` - Faza 1

```python
import re
from faker import Faker

fake = Faker('pl_PL')

TOKEN_GENERATORS = {
    # Dane osobowe
    "name", "surname", "first_name", "last_name",
    # Lokalizacja
    "city", "address" (tylko ulica z numerem), "street",
    # Kontakt
    "phone", "email", "username", "user-name",
    # Dokumenty
    "pesel", "document-number", "document_number", "id-number", "id_number", "nip", "regon",
    # Finanse
    "bank-account", "bank_account", "iban", "credit-card", "credit-card-number", "credit_card_number",
    # Inne
    "age", "sex", "company", "date", "data", "date-of-birth", "date_of_birth",
    "job", "job-title", "job_title", "school-name", "school_name",
    # Wrażliwe
    "political-view", "political_view", "health", "relative", "ethnicity",
    "religion", "sexual-orientation", "sexual_orientation", "secret",
}

# UWAGA: address zwraca TYLKO ulicę z numerem (np. "ul. Długa 15")
# bez kodu pocztowego i miasta, bo miasto jest osobno w [city]

def process_with_faker(text: str) -> str:
    """Faza 1: Zastąp tokeny [...] wartościami z Fakera."""
    def replace(match):
        token = match.group(1).lower().strip()
        generator = TOKEN_GENERATORS.get(token)
        return generator() if generator else match.group(0)
    
    return re.sub(r'\[([^\]]+)\]', replace, text)

def has_remaining_tokens(text: str) -> bool:
    """Sprawdź czy są jeszcze tokeny [...]."""
    return bool(re.search(r'\[([^\]]+)\]', text))
```

### 3. `core.py` - Pipeline

```python
from .faker_processor import process_with_faker, has_remaining_tokens
from .llm_client import fill_tokens, correct_morphology

def synthesize_line(line: str, use_llm: bool = True) -> dict:
    """
    Przetwórz jedną linię przez 3 fazy.
    
    Returns:
        {
            "original": str,
            "after_faker": str,
            "after_fill": str,
            "final": str,
            "phases_used": list
        }
    """
    result = {
        "original": line,
        "phases_used": []
    }
    
    # FAZA 1: Faker
    text = process_with_faker(line)
    result["after_faker"] = text
    result["phases_used"].append("faker")
    
    if not use_llm:
        result["final"] = text
        return result
    
    # FAZA 2: LLM Fill (tylko jeśli są tokeny)
    if has_remaining_tokens(text):
        text = fill_tokens(text)
        result["phases_used"].append("llm_fill")
    result["after_fill"] = text
    
    # FAZA 3: LLM Morphology
    text = correct_morphology(text)
    result["phases_used"].append("llm_morphology")
    result["final"] = text
    
    return result
```

---

## 🚀 CLI Interface

```bash
# Przetworz cały plik
uv run python main.py process ../nask_train/orig.txt -o output.txt

# Opcje dla process:
uv run python main.py process input.txt -o output.txt \
    --model "ollama/PRIHLOP/PLLuM:latest" \  # Model LLM
    --no-llm \                                # Tylko Faker (bez LLM)
    --no-jsonl \                              # Nie generuj .jsonl
    --prompt-mode                             # Użyj pełnych promptów zamiast dspy.Predict

# Testuj losową linijkę
uv run python main.py test --random

# Testuj konkretną linijkę (np. 21)
uv run python main.py test --line 21

# Testuj N losowych linijek
uv run python main.py test --random-n 5

# Opcje dla test:
uv run python main.py test --line 21 \
    --model "ollama/PRIHLOP/PLLuM:latest" \
    --no-llm \                                # Tylko Faker
    --prompt-mode                             # Pełne prompty

# Pokaż obsługiwane tokeny
uv run python main.py tokens

# Uruchom REST API
uv run python main.py serve --port 8000 --host 0.0.0.0
```

---

## 🌐 REST API

```python
# POST /synthesize
{
    "text": "Nazywam się [name] [surname], mieszkam w [city].",
    "use_llm": true
}

# Response
{
    "original": "Nazywam się [name] [surname], mieszkam w [city].",
    "synthetic": "Nazywam się Anna Kowalska, mieszkam w Warszawie.",
    "phases_used": ["faker", "llm_morphology"]
}

# POST /synthesize/batch
{
    "lines": ["...", "...", "..."],
    "use_llm": true
}
```

---

## 📊 Progress Bar i Zapis na Bieżąco

```python
from tqdm import tqdm

def process_file(input_path: str, output_path: str):
    # Otwórz pliki na początku (streaming write)
    txt_file = open(output_path, 'w', encoding='utf-8', buffering=1)  # Line buffering
    jsonl_file = open(output_path.replace('.txt', '.jsonl'), 'w', encoding='utf-8', buffering=1)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    try:
        for i, line in enumerate(tqdm(lines, desc="Synthesizing", unit="lines"), 1):
            result = synthesize_line(line)
            
            # Zapisuj natychmiast po przetworzeniu (na bieżąco)
            txt_file.write(result["final"] + '\n')
            txt_file.flush()
            
            json.dump({
                "line": i, 
                "original": result["original"], 
                "synthetic": result["final"],
                "phases": result["phases_used"]  # Dla debugowania
            }, jsonl_file, ensure_ascii=False)
            jsonl_file.write('\n')
            jsonl_file.flush()
    finally:
        txt_file.close()
        jsonl_file.close()
```

**Korzyści zapisu na bieżąco:**
- Wyniki widoczne natychmiast w pliku
- Jeśli proces się przerwie, nie tracimy już przetworzonych linii
- Możliwość monitorowania postępu przez sprawdzanie pliku wyjściowego

---

## 🔧 Konfiguracja

```yaml
# config.yaml
llm:
  model: "ollama/PRIHLOP/PLLuM:latest"  # lub "ollama/gemma3:12b"

faker:
  locale: "pl_PL"

output:
  generate_jsonl: true
```

---

## ⚡ Kluczowe Różnice od dawid_cli

| Aspekt | dawid_cli | synthesize |
|--------|-----------|------------|
| Linie kodu | ~1500 | ~300 |
| Konfiguracja LLM | Skomplikowana (online/local/direct API) | Prosta jak TestDspy |
| Flow | Niejasny, wiele warstw | 3 jasne fazy |
| Testowanie | Brak dedykowanego | Folder tests/ |
| REST API | Brak | Wbudowany |
| Progress | Tak | Tak |
| DSPy | Skomplikowane wywołania | dspy.Predict (proste) |

---

## 📝 Prompty

Prompty są zoptymalizowane zgodnie z best practices:
- **Few-shot examples** (wejście → wyjście)
- **Przykłady złych odpowiedzi** (czego NIE robić)
- **Wielokrotne przypomnienia** o formacie
- **Optymalizacja TEKST_JEST_TAKI_SAM** - jeśli tekst nie wymaga zmian

```python
# prompts.py

FILL_TOKENS_PROMPT = """
W tekście są tokeny w nawiasach kwadratowych (np. [name], [city]).
Podmień KAŻDY token na realistyczne polskie dane.

OPTYMALIZACJA:
Jeśli tekst NIE MA żadnych tokenów do uzupełnienia, 
zwróć TYLKO: TEKST_JEST_TAKI_SAM
To oszczędza tokeny!

Przykłady (wejście → wyjście):
- "Nazywam się [name] [surname]." → "Nazywam się Anna Kowalska."
- "Tekst bez tokenów." → "TEKST_JEST_TAKI_SAM"

KRYTYCZNE:
- Zwróć TYLKO tekst z tokenami lub "TEKST_JEST_TAKI_SAM"
- BEZ formatów JSON, BEZ komentarzy
"""

MORPHOLOGY_PROMPT = """
Sprawdź i popraw morfologię tekstu.

OPTYMALIZACJA:
Jeśli tekst NIE WYMAGA poprawek, zwróć: TEKST_JEST_TAKI_SAM

Przykłady poprawek:
- "Róża prosił o pomoc." → "Róża prosiła o pomoc."
- "Oliwier, kobieta" → "Oliwier, mężczyzna"
- "Poprawny tekst." → "TEKST_JEST_TAKI_SAM"

KRYTYCZNE ZASADY:
- NIE zmieniaj danych (imion, nazwisk, miast, numerów)
- Poprawiaj TYLKO formy gramatyczne
- Zwróć TYLKO tekst lub "TEKST_JEST_TAKI_SAM"
- BEZ formatów JSON, BEZ markdown (```)
"""
```

**Obsługa TEKST_JEST_TAKI_SAM w kodzie:**
- Jeśli LLM zwróci `TEKST_JEST_TAKI_SAM`, kod zwraca oryginalny tekst
- Oszczędza tokeny dla długich tekstów bez zmian

---

## 🧪 Testy

```python
# tests/test_random_line.py
"""Testuj losową linijkę z pliku."""

import random
from src.core import synthesize_line

def test_random_line(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    line_num = random.randint(1, len(lines))
    line = lines[line_num - 1]
    
    print(f"📍 Linia {line_num}/{len(lines)}")
    print(f"📝 ORIGINAL:\n{line}")
    
    result = synthesize_line(line)
    
    print(f"\n🔄 AFTER FAKER:\n{result['after_faker']}")
    print(f"\n✅ FINAL:\n{result['final']}")
    print(f"\n📊 Phases: {result['phases_used']}")

if __name__ == "__main__":
    test_random_line("../nask_train/orig.txt")
```

---

## 🛠️ Instalacja

```bash
cd synthesize
uv venv
uv pip install -e .

# Model Ollama (jeśli local)
ollama pull PRIHLOP/PLLuM:latest
```

---

## 📌 Podsumowanie

Ten moduł to **uproszczona, czytelna wersja** dawid_cli z:
1. **Jasnym 3-fazowym flow**
2. **Prostą konfiguracją DSPy** (jak TestDspy)
3. **Wbudowanym REST API**
4. **Dedykowanymi testami**
5. **~300 linii zamiast ~1500**

Cel: **Mniej kodu, więcej przejrzystości, ta sama funkcjonalność.**

