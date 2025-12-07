# Synthetic Generation - Generacja danych syntetycznych

## Mechanizm generacji

Nasze rozwiązanie wykorzystuje **3-fazowy pipeline** do generacji danych syntetycznych z zachowaniem poprawnej morfologii języka polskiego.

### Źródła danych

1. **Biblioteka Faker (pl_PL)** - podstawowe źródło syntetycznych danych:
   - Imiona i nazwiska polskie
   - Miasta i adresy
   - Numery PESEL, telefonów, e-maile
   - Nazwy firm, stanowisk

2. **Model językowy (LLM)** - dla wartości niestandardowych:
   - PLLuM API (online) lub lokalny Ollama (PLLuM, gpt-oss)
   - Uzupełnianie tokenów, które Faker nie obsługuje
   - Korekta morfologii całego zdania

## Walka z fleksją

### Problem

Język polski ma skomplikowaną fleksję. Przykład:
- **Problem:** Model widzi `Mieszkam w {city}` i zamienia na `Mieszkam w Radom` (błędna forma)
- **Sukces:** Zamienia na `Mieszkam w Radomiu` (poprawna forma miejscownika)

### Rozwiązanie

**Faza 3: LLM Morphology** - dedykowana faza korekty morfologii:

1. **Analiza kontekstu przez LLM:**
   - Model analizuje całe zdanie, nie tylko token
   - Rozpoznaje przypadek, liczbę, rodzaj wymagane przez kontekst

2. **Korekta form gramatycznych:**
   - Poprawa przypadków (mianownik → miejscownik: "Radom" → "Radomiu")
   - Zgodność rodzaju (imię męskie → czasownik w odpowiedniej formie)
   - Poprawa form czasowników ("Róża prosił" → "Róża prosiła")

3. **Optymalizacja:**
   - Jeśli tekst nie wymaga poprawek, LLM zwraca `TEKST_JEST_TAKI_SAM`
   - Oszczędność tokenów dla tekstów już poprawnych

### Przykłady poprawek morfologicznych

| Oryginał (po Fakerze) | Poprawiony (po LLM Morphology) |
|----------------------|-------------------------------|
| "Mieszkam w Radom" | "Mieszkam w Radomiu" |
| "Róża prosił o pomoc" | "Róża prosiła o pomoc" |
| "Oliwier, kobieta" | "Oliwier, mężczyzna" |

## Dbałość o sens

### Zachowanie kontekstu

1. **Spójność danych:**
   - Imię męskie → płeć męska w całym zdaniu
   - Miasto w miejscowniku → poprawna forma fleksyjna
   - Nazwisko → odpowiednia odmiana

2. **Realistyczność:**
   - Generowane dane są realistyczne (prawdziwe polskie imiona, miasta)
   - Numery PESEL są poprawnie sformatowane
   - Adresy są kompletne i spójne

3. **Zachowanie struktury:**
   - Nie zmieniamy struktury zdania
   - Nie dodajemy ani nie usuwamy informacji
   - Tylko zastępujemy tokeny na syntetyczne dane

### Randomizacja

- Randomizacja odbywa się na poziomie wartości, nie struktury
- Każde uruchomienie może wygenerować inne wartości
- Struktura i sens zdania pozostają zachowane

## Log z przykładami (Showcase)

### Przykład 1: Podstawowa anonimizacja i synteza

**Szablon (zanonimizowany):**
```
Nazywam się [name] [surname], mój PESEL to [pesel]. Mieszkam w [address].
```

**Wynik (syntetyczny):**
```
Nazywam się Maria Nowak, mój PESEL to 12432486324. Mieszkam w Bielsku-Białej przy ulicy Szerokiej 5.
```

### Przykład 2: Fleksja miejscownika

**Szablon (zanonimizowany):**
```
Spotkałem się z [name] w [city].
```

**Wynik (syntetyczny):**
```
Spotkałem się z Kasią w Gdańsku.
```

**Uwaga:** Poprawna forma miejscownika "Gdańsku" (nie "Gdańsk")

### Przykład 3: Zgodność rodzaju

**Szablon (zanonimizowany):**
```
[name] [surname] prosił o pomoc w sprawie [document-number].
```

**Wynik (syntetyczny):**
```
Jan Kowalski prosił o pomoc w sprawie ABC123456.
```

**Alternatywnie (imię żeńskie):**
```
Anna Kowalska prosiła o pomoc w sprawie ABC123456.
```

**Uwaga:** Poprawna forma czasownika zgodna z rodzajem imienia

### Przykład 4: Kompleksowy adres

**Szablon (zanonimizowany):**
```
Mój adres to [address], kod pocztowy [postal-code], miasto [city].
```

**Wynik (syntetyczny):**
```
Mój adres to ulica Długa 15, kod pocztowy 00-001, miasto Warszawa.
```

### Przykład 5: Dane wrażliwe

**Szablon (zanonimizowany):**
```
Moja [relative] [name] [surname] mieszka w [city] i pracuje w [company].
```

**Wynik (syntetyczny):**
```
Moja siostra Anna Kowalska mieszka w Krakowie i pracuje w Tech Solutions Sp. z o.o..
```

**Uwaga:** 
- Poprawna forma miejscownika "Krakowie"
- Spójność danych (imię żeńskie → "siostra")
- Realistyczna nazwa firmy

## Architektura techniczna

### Pipeline 3-fazowy

```
Input: "[name] [surname] mieszka w [city]"
  ↓
Faza 1 (Faker): "Anna Kowalska mieszka w Warszawa"
  ↓
Faza 2 (LLM Fill): [Pominięta - wszystkie tokeny zastąpione]
  ↓
Faza 3 (LLM Morphology): "Anna Kowalska mieszka w Warszawie"
  ↓
Output: "Anna Kowalska mieszka w Warszawie"
```

### Obsługiwane tokeny

Moduł obsługuje wszystkie tokeny wymagane w zadaniu:
- `[name]`, `[surname]`, `[age]`, `[date-of-birth]`, `[date]`, `[sex]`
- `[city]`, `[address]`, `[email]`, `[phone]`
- `[pesel]`, `[document-number]`
- `[company]`, `[school-name]`, `[job-title]`
- `[bank-account]`, `[credit-card-number]`
- `[username]`, `[secret]`
- `[religion]`, `[political-view]`, `[ethnicity]`, `[sexual-orientation]`, `[health]`, `[relative]`

## Wydajność

- **Faza 1 (Faker):** ~0.001s na linię (bardzo szybka)
- **Faza 2 (LLM Fill):** ~1-3s na linię (tylko jeśli potrzebna)
- **Faza 3 (LLM Morphology):** ~1-3s na linię
- **Optymalizacja:** Faza 2 jest pomijana jeśli wszystkie tokeny zostały zastąpione przez Faker

## Tryby pracy

1. **Tylko Faker** (`--no-llm`): Szybkie, ale bez korekty morfologii
2. **Pełny pipeline** (domyślny): Faker + LLM Fill + LLM Morphology
3. **Online** (`--online`): Użycie PLLuM API zamiast lokalnego modelu

