# Podsumowanie Projektu: PLLuM Anonymizer

## 🎯 Cel Projektu

Stworzenie skalowalnego, działającego offline narzędzia do anonimizacji danych osobowych (PII) dla języka polskiego, zgodnie z wymogami projektu PLLuM. System zastępuje dane osobowe syntetycznymi danymi, zachowując poprawność morfologiczną i kontekst.

## 📋 Wymagania Architektoniczne

### Framework Bazowy
- **Presidio** (`microsoft/presidio`) - szkielet do detekcji i anonimizacji PII
- **GLiNER** (`urchade/gliner_small-v2.1`) - zero-shot NER do wykrywania trudnych kategorii
- **Spacy** (`pl_core_news_lg`) - analiza morfologiczna (lematyzacja, przypadek, liczba, rodzaj)
- **Faker** (`pl_PL`) - generowanie syntetycznych danych

### Warstwy Detekcji
1. **Warstwa 1 (Szybka)**: Regex dla PESEL, NIP, Email, Telefonów, Kart kredytowych
2. **Warstwa 2 (Kontekstowa)**: GLiNER do wykrywania kategorii: `{political-view}`, `{health}`, `{relative}`, `{city}` vs `{address}`

### Tryby Anonimizacji
1. **Tryb prosty**: Zastąpienie tokenem (np. `[name]` → `{name}`)
2. **Tryb zaawansowany (Data Synthesis)**: Generowanie polsko brzmiących zamienników z zachowaniem fleksji

## 🏗️ Struktura Projektu

```
/pllum-anonymizer (dawid_cli)
│
├── requirements.txt          # Zależności Python
├── config.yaml               # Konfiguracja etykiet, ścieżek do modeli, LLM
├── prompts.yaml              # Prompty dla LLM (łatwa edycja)
├── env.template              # Szablon zmiennych środowiskowych
├── process_file.py           # Główny skrypt CLI do przetwarzania plików
│
├── src/
│   ├── __init__.py
│   ├── analyzer_engine.py    # Klasa dziedzicząca po Presidio, integruje GLiNER i Regexy
│   ├── recognizers/          # Customowe recognizery
│   │   ├── __init__.py
│   │   ├── gliner_recognizer.py  # Wrapper na model GLiNER dla Presidio
│   │   └── regex_patterns.py     # Wzorce dla PESEL, Dowodów, Kont itp.
│   │
│   └── synthesis/            # Moduł generacji danych syntetycznych
│       ├── __init__.py
│       ├── morph_generator.py    # Logika Faker + Spacy/Morfeusz do odmiany
│       └── custom_operators.py    # Operatory dla Presidio Anonymizer
│
└── tests/                    # Testy jednostkowe
    ├── test_pipeline.py
    ├── test_comparison.py
    └── test_simple.py
```

## ✅ Co Zostało Zaimplementowane

### 1. **Moduł Generacji Syntetycznych Danych** (`morph_generator.py`)

#### Funkcjonalności:
- ✅ Generowanie danych przez Faker (imiona, nazwiska, miasta, adresy, telefony, emaile, PESEL, itp.)
- ✅ Analiza morfologiczna przez Spacy (przypadek, liczba, rodzaj)
- ✅ Integracja z LLM (PLLuM API lub lokalny Ollama) do poprawy morfologii
- ✅ Zachowanie spójności kontekstowej (np. imię męskie → płeć męska)
- ✅ Analiza kontekstu przez LLM (rozróżnianie `[name]` jako osoba vs. część adresu)

#### Kluczowe Metody:
- `generate()` - główna metoda generacji z routingiem do odpowiednich generatorów
- `_generate_with_llm()` - generowanie przez LLM z promptami z `prompts.yaml`
- `_analyze_context_with_llm()` - analiza kontekstu tokenu (osoba/adres/miejscowość)
- `generate_name()`, `generate_city()`, `generate_address()`, itp. - specyficzne generatory

### 2. **CLI Tool** (`process_file.py`)

#### Funkcjonalności:
- ✅ Przetwarzanie plików `.txt` z tokenami PII (np. `[name]`, `[city]`)
- ✅ Generowanie wersji zanonimizowanej (`.txt` + `.jsonl`)
- ✅ Tryb sample (`--sample N`) - losowy wybór N linii z porównaniem 3 wersji:
  - Oryginalna
  - Po Fakerze (bez LLM)
  - Po weryfikacji LLM
- ✅ Pasek postępu (`tqdm`)
- ✅ Obsługa błędów z logowaniem

#### Przykłady użycia:
```bash
# Przetwarzanie wszystkich linii
python process_file.py ../nask_train/orig.txt

# Tryb sample (testowanie)
python process_file.py ../nask_train/orig.txt --sample 3

# Własne pliki wejściowe/wyjściowe
python process_file.py input.txt output.txt
```

### 3. **Konfiguracja LLM**

#### Tryby:
- ✅ **Online** (PLLuM API) - domyślny
- ✅ **Local** (Ollama) - `PRIHLOP/PLLuM:latest`
- ✅ **None** - tylko Faker, bez LLM

#### Pliki konfiguracyjne:
- `config.yaml` - ustawienia LLM, entity labels, ścieżki do modeli
- `prompts.yaml` - wszystkie prompty dla LLM (łatwa edycja)
- `.env` - klucze API, tryb LLM

### 4. **System Promptów**

#### Struktura (`prompts.yaml`):
- `system_prompt` - ogólne instrukcje dla LLM
- `context_analysis_prompt` - analiza kontekstu tokenu
- `entity_prompts` - prompty dla każdego typu encji (`{name}`, `{city}`, itp.)
- `default_prompt` - fallback dla nieznanych typów

#### Kluczowe założenia promptów:
- LLM wie, że dane są wstępnie wygenerowane przez Faker
- LLM poprawia morfologię (przypadek, liczba, rodzaj)
- LLM uzupełnia pozostałości tokenów (np. `[name]`, `[city]`)
- Tokeny są w formacie `[name]`, nie `{name}`

### 5. **Obsługa Morfologii**

#### Implementacja:
- ✅ Integracja ze Spacy (`pl_core_news_lg`) do analizy morfologicznej
- ✅ Ekstrakcja cech: przypadek, liczba, rodzaj
- ✅ Próba zachowania formy gramatycznej (uproszczona, docelowo Morfeusz)
- ✅ Spójność płci (imię → płeć)

#### Ograniczenia:
- Spacy nie obsługuje pełnej odmiany polskich słów
- Docelowo potrzebny Morfeusz2 dla pełnej fleksji
- Obecnie: proste heurystyki + LLM do poprawy

### 6. **Testy**

#### Zaimplementowane:
- ✅ `test_simple.py` - testy jednostkowe generatorów
- ✅ `test_comparison.py` - porównanie z plikami referencyjnymi
- ✅ Testy spójności płci
- ✅ Testy formatów (telefon, email, PESEL)

## ⚠️ Problemy z Wydajnością (Czas Realizacji)

### 1. **Sekwencyjne Przetwarzanie**
- **Problem**: Każda linia jest przetwarzana sekwencyjnie
- **Przyczyna**: 
  - LLM jest bottleneck (każde wywołanie to request HTTP)
  - GIL w Pythonie (wątki nie pomagają dla CPU-bound)
  - Kontekst między tokenami wymaga sekwencyjności
- **Wpływ**: Dla 3000 linii z LLM → ~30-60 minut (zależnie od API)

### 2. **Wielokrotne Wywołania LLM**
- **Problem**: Dla każdego tokena `[name]`, `[city]` itp. → osobne wywołanie LLM
- **Przykład**: Linia z 5 tokenami = 5 wywołań LLM
- **Wpływ**: 
  - 3000 linii × średnio 3 tokeny = ~9000 wywołań LLM
  - Każde wywołanie: ~1-3 sekundy (zależnie od API)
  - **Całkowity czas: ~2.5-7.5 godzin**

### 3. **Analiza Kontekstu**
- **Problem**: Dla każdego `[name]` → dodatkowe wywołanie LLM do analizy kontekstu
- **Wpływ**: Podwaja liczbę wywołań dla tokenów `name`, `city`, `address`

### 4. **Brak Batch Processing**
- **Problem**: Nie ma możliwości przetwarzania wielu tokenów jednocześnie
- **Możliwe rozwiązanie**: Batch requests do LLM (jeśli API wspiera)

### 5. **Brak Cache'owania**
- **Problem**: Te same tokeny są generowane wielokrotnie
- **Możliwe rozwiązanie**: Cache dla często występujących tokenów

## 📊 Metryki Wydajności

### Obecna Wydajność (szacunkowo):
- **Bez LLM (tylko Faker)**: ~100-200 linii/sekundę
- **Z LLM (online API)**: ~1-2 linie/sekundę (zależnie od liczby tokenów)
- **Z LLM (local Ollama)**: ~0.5-1 linia/sekundę

### Dla Pliku 3000 Linii:
- **Tylko Faker**: ~15-30 sekund ✅
- **Z LLM (online)**: ~25-50 minut ⚠️
- **Z LLM (local)**: ~50-100 minut ⚠️⚠️

## 🔧 Możliwe Optymalizacje

### 1. **Batch Processing**
- Grupowanie tokenów z wielu linii
- Jedno wywołanie LLM dla wielu tokenów
- **Szacowany zysk**: 5-10x szybsze

### 2. **Cache'owanie**
- Cache dla często występujących tokenów
- **Szacowany zysk**: 2-3x szybsze dla powtarzających się danych

### 3. **Równoległe Przetwarzanie (z ograniczeniami)**
- Batch requests do API (jeśli wspiera)
- **Szacowany zysk**: 3-5x szybsze

### 4. **Inteligentne Użycie LLM**
- LLM tylko dla tokenów wymagających morfologii
- Faker dla prostych danych (telefon, email, PESEL)
- **Szacowany zysk**: 2-3x szybsze

### 5. **Lokalny Model (Ollama)**
- Szybsze niż API (brak network latency)
- Ale wolniejsze niż API (mniejszy model)
- **Szacowany zysk**: Zależnie od modelu

## 📝 Status Implementacji

### ✅ Zrobione:
- [x] Struktura projektu
- [x] Moduł generacji syntetycznych danych (Faker + Spacy)
- [x] Integracja z LLM (online + local)
- [x] System promptów (konfigurowalny)
- [x] CLI tool z trybem sample
- [x] Obsługa morfologii (podstawowa)
- [x] Analiza kontekstu przez LLM
- [x] Testy jednostkowe
- [x] Dokumentacja

### ⚠️ Częściowo Zrobione:
- [ ] Pełna integracja z Presidio (szkielet jest, ale nie używany w głównym flow)
- [ ] GLiNER recognizer (zdefiniowany, ale nie zintegrowany)
- [ ] Morfeusz2 dla pełnej fleksji (uproszczone heurystyki)

### ❌ Nie Zrobione:
- [ ] Batch processing dla LLM
- [ ] Cache'owanie wyników
- [ ] Optymalizacja wydajności
- [ ] Pełna integracja z Presidio Analyzer
- [ ] GUI/web interface

## 🎯 Rekomendacje

### Dla Szybkiego Działania:
1. **Użyj tylko Faker** dla prostych przypadków (bez morfologii)
2. **LLM tylko dla krytycznych tokenów** (imiona, miasta wymagające odmiany)
3. **Batch processing** - priorytet #1 dla optymalizacji

### Dla Pełnej Funkcjonalności:
1. **Integracja Morfeusz2** dla pełnej fleksji
2. **Cache'owanie** często występujących tokenów
3. **Batch API requests** jeśli API wspiera
4. **Monitoring wydajności** - metryki czasu przetwarzania

## 📚 Technologie

- **Python 3.8+**
- **Presidio** (2.2.0+)
- **GLiNER** (0.2.0+)
- **Spacy** (3.8.0+) + `pl_core_news_lg`
- **Faker** (24.0.0+) + locale `pl_PL`
- **LangChain** (OpenAI + Ollama)
- **YAML** (konfiguracja)
- **tqdm** (progress bar)

## 🔗 Pliki Kluczowe

- `src/synthesis/morph_generator.py` - główna logika generacji
- `process_file.py` - CLI tool
- `prompts.yaml` - prompty LLM (łatwa edycja)
- `config.yaml` - konfiguracja systemu
- `requirements.txt` - zależności

---

**Data utworzenia**: 2024
**Status**: Funkcjonalny, wymaga optymalizacji wydajności
**Główny problem**: Czas przetwarzania z LLM (sekwencyjne wywołania API)

