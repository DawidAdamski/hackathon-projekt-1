# Tests

Folder zawiera testy dla modułu generowania syntetycznych danych.

## Testy

### test_comparison.py
Porównuje wygenerowane dane z oryginalnymi plikami:
- `orig.txt` - oryginał z tokenami `[name]`, `[city]`, etc.
- `anonymized.txt` - zanonimizowany z prawdziwymi danymi
- `anonymized_synthetic.txt` - nasz wygenerowany z Fakerem

**Uruchomienie:**
```bash
python tests/test_comparison.py
```

Test sprawdza:
- Czy wszystkie tokeny zostały zastąpione
- Statystyki użycia różnych typów tokenów
- Porównanie wyników z `anonymized.txt`
- Przykładowe porównania linii

### test_simple.py
Podstawowe testy jednostkowe dla `MorphologicalGenerator`.

**Uruchomienie:**
```bash
python tests/test_simple.py
```

## Wymagania

Przed uruchomieniem testów upewnij się, że:
1. Wygenerowałeś plik `anonymized_synthetic.txt`:
   ```bash
   python process_file.py
   ```
2. Pliki `orig.txt` i `anonymized.txt` znajdują się w `nask_train/`

