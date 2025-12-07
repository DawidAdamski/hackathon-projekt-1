# Preprocessing - Opis przetwarzania i pozyskiwania danych

## Podejście do anonimizacji

Nasze rozwiązanie wykorzystuje **hybrydowe podejście** łączące:
- **RegEx** dla struktur o stałej formie (PESEL, numery dokumentów, e-maile, telefony)
- **Analiza morfologiczna** (spaCy z modelem `pl_nask`) dla poprawnej detekcji w różnych odmianach fleksyjnych
- **Biblioteka priv_masker** dla wykrywania i maskowania danych osobowych

## Proces przetwarzania

### 1. Moduł anonimizacji (Część 1)

**Warstwa 1 - Szybka detekcja (RegEx):**
- Numery PESEL (11 cyfr)
- Numery dokumentów (dowód, paszport, prawo jazdy)
- Adresy e-mail
- Numery telefonów
- Numery kart kredytowych
- Numery kont bankowych (IBAN)

**Warstwa 2 - Kontekstowa detekcja (spaCy + priv_masker):**
- Imiona i nazwiska w różnych odmianach (wykrywane przez spaCy NER)
- Rozróżnianie `{city}` vs `{address}` na podstawie kontekstu i wzorców
- Wykrywanie danych wrażliwych: `{health}`, `{political-view}`, `{relative}`, etc. (poprzez analizę kontekstu)

**Zastępowanie:**
- Wszystkie wykryte dane osobowe są zastępowane tokenami w formacie `[name]`, `[surname]`, `[pesel]`, etc.
- Format zgodny z wymaganiami zadania (nawiasy kwadratowe)

### 2. Moduł syntezy danych (Część 2 - `synthesize`)

**Faza 1: Faker**
- Szybkie zastąpienie tokenów wartościami z biblioteki Faker (pl_PL)
- Obsługa większości standardowych tokenów (imiona, nazwiska, miasta, adresy, PESEL, etc.)

**Faza 2: LLM Fill (warunkowo)**
- Uzupełnienie tokenów, które Faker nie obsłużył
- Użycie modelu językowego (PLLuM lub lokalny Ollama) do generacji brakujących wartości

**Faza 3: LLM Morphology**
- Korekta morfologii całego zdania
- Poprawa przypadków, form czasowników, zgodności rodzaju
- Zapewnienie poprawności gramatycznej

## Pozyskiwanie danych

- **Biblioteka Faker** (`pl_PL`) - generowanie syntetycznych danych polskich
- **Słowniki polskie** - dla imion, nazwisk, miast
- **Model językowy** - dla wartości niestandardowych i poprawy morfologii

## Czyszczenie danych

- Zachowanie struktury oryginalnego tekstu
- Nie usuwanie zdań - tylko zastępowanie danych osobowych
- Zachowanie kolejności linii (1:1 z plikiem wejściowym)

