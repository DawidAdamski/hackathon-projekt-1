# Wymagane pliki do oceny

Ten folder zawiera pliki wymagane do wgrania na platformę ChallengeRocket.

## Pliki wymagane

1. **output_Application_Fail_Successfully.txt** - Zanonimizowany plik wynikowy
   - Format 1:1 z plikiem wejściowym
   - Tokeny w nawiasach kwadratowych: `[name]`, `[pesel]`, `[city]`, etc.

2. **performance_Application_Fail_Successfully.txt** - Czas i opis sprzętu
   - Czas przetwarzania
   - Specyfikacja sprzętu (CPU/GPU)
   - Informacje o użyciu API

3. **preprocessing_Application_Fail_Successfully.md** - Opis przetwarzania danych (opcjonalne)

4. **synthetic_generation_Application_Fail_Successfully.md** - Opis metody generacji danych syntetycznych
   - Punktowane w sekcji związanej z modułem generacji danych syntetycznych

5. **presentation_Application_Fail_Successfully.pdf** - Prezentacja (max 5 slajdów)
   - Wymagane
   - Ocena pomysłowości podejścia
   - **Pomocniczy plik:** `presentation_Application_Fail_Successfully.md` zawiera treść do prezentacji

## Instrukcja

**WAŻNE:** Przed wgraniem plików na platformę ChallengeRocket:

1. Wypełnij wszystkie pliki zgodnie z wymaganiami:
   - `performance_Application_Fail_Successfully.txt` - uzupełnij dane o wydajności
   - `output_Application_Fail_Successfully.txt` - wygeneruj używając modułu anonimizacji

2. Przygotuj prezentację PDF (max 5 slajdów):
   - Użyj treści z `presentation_Application_Fail_Successfully.md` jako podstawy
   - Stwórz plik PDF `presentation_Application_Fail_Successfully.pdf`

## Struktura plików

```
wymagane_pliki/
├── README.md (ten plik)
├── output_Application_Fail_Successfully.txt
├── performance_Application_Fail_Successfully.txt
├── preprocessing_Application_Fail_Successfully.md
├── synthetic_generation_Application_Fail_Successfully.md
├── presentation_Application_Fail_Successfully.md (pomocniczy - treść do PDF)
└── presentation_Application_Fail_Successfully.pdf (do stworzenia)
```

