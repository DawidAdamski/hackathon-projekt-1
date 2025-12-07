# Sprawdzanie trybu LLM

## Jak sprawdzić który tryb jest aktywny:

### 1. Sprawdź config.yaml:
```yaml
llm:
  mode: "online"  # lub "local"
```

### 2. Sprawdź output przy starcie:
- **Online**: `✓ LLM initialized (online mode: CYFRAGOVPL/pllum-12b-nc-chat-250715)`
- **Local**: `✓ LLM initialized (local mode: PRIHLOP/PLLuM:latest)`

### 3. Sprawdź czy Ollama działa:
```bash
# Windows PowerShell
curl http://localhost:11434/api/tags

# Lub sprawdź czy proces działa
Get-Process ollama -ErrorAction SilentlyContinue
```

## Jak przełączyć na lokalny Ollama:

### Krok 1: Zmień config.yaml
```yaml
llm:
  mode: "local"  # zmień z "online" na "local"
```

### Krok 2: Zainstaluj langchain-ollama
```bash
uv pip install langchain-ollama
```

### Krok 3: Uruchom Ollama
```bash
ollama serve
```

### Krok 4: Pobierz model
```bash
ollama pull PRIHLOP/PLLuM:latest
```

### Krok 5: Sprawdź czy działa
```bash
python process_file.py ../nask_train/orig.txt --sample 1
```

Powinieneś zobaczyć: `✓ LLM initialized (local mode: PRIHLOP/PLLuM:latest)`

