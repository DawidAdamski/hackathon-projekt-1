# Quick Start - Generowanie Syntetycznych Danych

## Proste użycie (bez Spacy)

Jeśli potrzebujesz tylko podstawowego fakowania danych **bez zachowania morfologii**, możesz użyć generatora bez Spacy:

```python
from src.synthesis.morph_generator import MorphologicalGenerator

# Proste fakowanie bez Spacy (szybsze, mniejsze wymagania)
generator = MorphologicalGenerator(use_morphology=False)

# Generowanie danych
name = generator.generate("[name]", "{name}")
city = generator.generate("[city]", "{city}")
phone = generator.generate("[phone]", "{phone}")
email = generator.generate("[email]", "{email}")

print(f"Imię: {name}")
print(f"Miasto: {city}")
print(f"Telefon: {phone}")
print(f"Email: {email}")
```

## Z morfologią (wymaga Spacy)

Jeśli chcesz zachować formy gramatyczne (przypadek, liczba):

```python
# Z morfologią (wymaga zainstalowanego modelu Spacy)
generator = MorphologicalGenerator(use_morphology=True)
```

## Przetwarzanie pliku

```bash
# Automatycznie użyje Spacy jeśli dostępne, w przeciwnym razie prosty tryb
python process_file.py ../nask_train/orig.txt

# Lub z własnymi ścieżkami
python process_file.py ../nask_train/orig.txt output.txt
```

## Obsługiwane typy encji

- `{name}` - Imię
- `{surname}` - Nazwisko  
- `{city}` - Miasto
- `{address}` - Adres
- `{phone}` - Telefon
- `{email}` - Email
- `{pesel}` - PESEL
- `{document-number}` - Numer dowodu
- `{age}` - Wiek
- `{sex}` - Płeć
- `{company}` - Firma
- `{date}` - Data
- `{bank-account}` - Konto bankowe

## Wymagania

### Minimalne (bez morfologii):
```bash
uv pip install faker
```

### Pełne (z morfologią):
```bash
uv pip install -r requirements.txt
python -m spacy download pl_core_news_lg
```

## Użycie z LLM (opcjonalne)

1. Skopiuj `env.template` do `.env` i ustaw klucz API
2. Użyj:
   ```python
   generator = MorphologicalGenerator(use_llm=True, use_morphology=False)
   ```

## Przykłady

Zobacz `example_usage.py` dla więcej przykładów.
