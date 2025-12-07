# PLLuM Anonymizer - Moduł Synthesis

Moduł do generowania syntetycznych danych dla języka polskiego z zachowaniem morfologii.

## Instalacja

1. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

2. Zainstaluj model Spacy dla języka polskiego:
```bash
python -m spacy download pl_core_news_lg
```

Jeśli model `pl_core_news_lg` nie jest dostępny, można użyć mniejszego modelu:
```bash
python -m spacy download pl_core_news_md
```

3. (Opcjonalnie) Skonfiguruj LLM dla bardziej zaawansowanego generowania:
   - Skopiuj `env.template` do `.env`
   - Wypełnij wartości w pliku `.env`:
     ```bash
     cp env.template .env
     # Edytuj .env i ustaw PLLUM_API_KEY
     ```

## Struktura projektu

```
dawid_cli/
├── requirements.txt          # Zależności projektu
├── config.yaml               # Konfiguracja etykiet i modeli
├── src/
│   ├── __init__.py
│   └── synthesis/            # Moduł generacji syntetycznych danych
│       ├── __init__.py
│       ├── morph_generator.py      # Generator z morfologią
│       └── custom_operators.py     # Operatory dla Presidio
├── example_usage.py          # Przykłady użycia
└── process_file.py           # Skrypt do przetwarzania plików
```

## Użycie

### Podstawowe użycie (Faker)

```python
from src.synthesis.morph_generator import MorphologicalGenerator

# Inicjalizacja generatora (używa Faker)
generator = MorphologicalGenerator()

# Generowanie syntetycznych danych
name = generator.generate("[name]", "{name}")
city = generator.generate("Warszawie", "{city}")  # Próbuje zachować przypadek
phone = generator.generate("[phone]", "{phone}")
```

### Użycie z LLM (opcjonalne)

```python
from src.synthesis.morph_generator import MorphologicalGenerator

# Inicjalizacja z LLM (wymaga konfiguracji w .env)
generator = MorphologicalGenerator(use_llm=True)

# Generowanie z kontekstem (LLM może lepiej dopasować dane do kontekstu)
context = "Nazywam się [name] Kowalski, mieszkam w [city]"
name = generator.generate("[name]", "{name}", context=context, prefer_llm=True)
city = generator.generate("[city]", "{city}", context=context, prefer_llm=True)
```

LLM jest używany automatycznie, jeśli:
- `USE_LLM_FOR_SYNTHESIS=true` w pliku `.env`, lub
- `use_llm=True` jest przekazane do konstruktora, lub
- `prefer_llm=True` jest użyte w metodzie `generate()`

### Przetwarzanie pliku orig.txt

```bash
python process_file.py --input nask_train/orig.txt --output nask_train/anonymized_synthetic.txt
```

Lub z domyślnymi ścieżkami:
```bash
python process_file.py
```

### Przykłady użycia

Uruchom przykładowy skrypt:
```bash
python example_usage.py
```

## Obsługiwane typy encji

Moduł obsługuje następujące typy encji:

- `{name}` - Imię
- `{surname}` - Nazwisko
- `{city}` - Miasto (z próbą zachowania przypadka)
- `{address}` - Adres
- `{phone}` - Numer telefonu
- `{email}` - Adres email
- `{pesel}` - Numer PESEL
- `{document-number}` - Numer dowodu osobistego
- `{age}` - Wiek
- `{sex}` - Płeć
- `{company}` - Nazwa firmy
- `{date}` - Data
- `{bank-account}` - Numer konta bankowego

## Morfologia

Moduł próbuje zachować formy morfologiczne (przypadek, liczba, rodzaj) używając:
- **Spacy** do analizy morfologicznej
- **Faker** do generowania danych
- Prosty mapping końcówek jako fallback (docelowo powinien być użyty Morfeusz)

### Uwagi dotyczące morfologii

Obecna implementacja używa prostego mapowania końcówek. Dla pełnej obsługi odmiany polskich słów zalecane jest użycie biblioteki **Morfeusz2**, która wymaga dodatkowej instalacji i konfiguracji.

## Integracja z Presidio

Moduł zawiera operatory dla Presidio Anonymizer:

```python
from src.synthesis.custom_operators import SyntheticReplaceOperator, create_synthetic_operator_config

# Utworzenie operatora
operator = SyntheticReplaceOperator()

# Użycie z Presidio
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

config = create_synthetic_operator_config(
    entity_type="PERSON",
    custom_entity_type="{name}"
)
```

## Konfiguracja

Plik `config.yaml` zawiera:
- Mapowanie etykiet encji
- Ścieżki do modeli (Spacy, GLiNER)
- Ustawienia syntezy

## Wymagania

- Python 3.8+
- presidio-analyzer >= 2.2.0
- presidio-anonymizer >= 2.2.0
- spacy >= 3.8.0
- faker >= 24.0.0
- numpy >= 1.24.0
- pyyaml >= 6.0

### Opcjonalne (dla LLM)

- langchain-openai >= 0.1.0
- python-dotenv >= 1.0.0

## Konfiguracja LLM

Moduł obsługuje opcjonalną integrację z modelem językowym PLLuM dla bardziej kontekstowego generowania danych.

### Konfiguracja

1. Skopiuj plik `env.template` do `.env`:
   ```bash
   cp env.template .env
   ```

2. Edytuj `.env` i ustaw:
   ```env
   PLLUM_API_KEY=twoj_klucz_api
   PLLUM_BASE_URL=https://apim-pllum-tst-pcn.azure-api.net/vllm/v1
   PLLUM_MODEL_NAME=CYFRAGOVPL/pllum-12b-nc-chat-250715
   USE_LLM_FOR_SYNTHESIS=true
   ```

3. Użyj generatora z LLM:
   ```python
   generator = MorphologicalGenerator(use_llm=True)
   ```

### Testowanie integracji LLM

Uruchom skrypt testowy:
```bash
python test_llm_integration.py
```

### Zalety użycia LLM

- **Lepsze dopasowanie kontekstowe**: LLM może generować dane lepiej pasujące do kontekstu zdania
- **Zachowanie morfologii**: LLM lepiej radzi sobie z odmianą polskich słów
- **Naturalność**: Generowane dane są bardziej naturalne i spójne

### Fallback

Jeśli LLM nie jest dostępny lub wystąpi błąd, system automatycznie przełącza się na Faker.

## Rozwój

### Dodawanie nowych typów encji

1. Dodaj mapowanie w `config.yaml`
2. Zaimplementuj metodę `generate_*` w `MorphologicalGenerator`
3. Dodaj do słownika `generators` w metodzie `generate()`

### Ulepszanie morfologii

Aby poprawić obsługę morfologii, można:
1. Zintegrować bibliotekę Morfeusz2
2. Użyć API do odmiany (np. Morfeusz REST API)
3. Rozbudować mapping końcówek

## Licencja

Projekt PLLuM.

