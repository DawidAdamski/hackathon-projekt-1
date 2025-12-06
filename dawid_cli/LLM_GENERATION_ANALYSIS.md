# Analiza Generowania przez LLM

## Gdzie LLM generuje dane:

### 1. **`_fill_missing_tokens_with_llm()`** (linia ~260)
- **Cel**: Uzupełnia brakujące tokeny `[name]`, `[city]`, itp.
- **Warunek**: Wykonywany TYLKO jeśli są tokeny `[ ]` w tekście
- **Wywołanie**: `self.llm.invoke(messages)` lub `self.llm.invoke(user_prompt)`
- **Lokalizacja**: `src/synthesis/morph_generator.py:283` lub `285`

### 2. **`_correct_morphology_with_llm()`** (linia ~339)
- **Cel**: Poprawia morfologię (przypadek, liczba, rodzaj)
- **Warunek**: ZAWSZE wykonywany (jeśli LLM dostępny)
- **Wywołanie**: `self.llm.invoke(messages)` lub `self.llm.invoke(user_prompt)`
- **Lokalizacja**: `src/synthesis/morph_generator.py:369` lub `371`

### 3. **`_generate_with_llm()`** (linia ~441) - NIE UŻYWANY w nowym flow
- **Cel**: Stare wywołanie - obecnie nie używane w głównym flow
- **Status**: Zastąpione przez dwa osobne procesy powyżej

## Flow generowania:

```
Input → Faker → _fill_missing_tokens_with_llm() → _correct_morphology_with_llm() → Output
```

## Problem z GPU:

### Dla Online API (ChatOpenAI):
- **Nie używa GPU lokalnie** - to jest API call do serwera
- GPU jest po stronie serwera (PLLuM API)
- Lokalnie tylko HTTP request/response

### Dla Local Ollama:

**Opcja 1: ChatOllama (LangChain)**
- **Ollama automatycznie optymalizuje GPU** jeśli dostępne (zgodnie z [dokumentacją LangChain](https://docs.langchain.com/oss/python/integrations/chat/ollama))
- Ale może nie wymuszać GPU tak jak `ollama run`
- ChatOllama używa LangChain wrapper, który może używać innego endpointu

**Opcja 2: Bezpośrednie API (nasze rozwiązanie)**
- **Używa tego samego API co `ollama run`** - `/api/chat`
- **Wymusza użycie GPU** - działa identycznie jak `ollama run`
- Ustaw `OLLAMA_USE_DIRECT_API=true` w `.env`

## Sprawdzenie czy LLM jest wywoływany:

### Debug - dodaj print przed wywołaniem:
```python
print(f"DEBUG: Calling LLM with prompt length: {len(user_prompt)}")
response = self.llm.invoke(messages)
print(f"DEBUG: LLM response received")
```

### Sprawdź czy proces 1 jest wywoływany:
- Jeśli nie ma tokenów `[ ]` → proces 1 jest pomijany
- Sprawdź czy w tekście są tokeny po Fakerze

### Sprawdź czy proces 2 jest wywoływany:
- Proces 2 jest ZAWSZE wywoływany (jeśli LLM dostępny)
- Sprawdź czy `_correct_morphology_with_llm()` jest wywoływana

## Możliwe przyczyny braku użycia GPU:

1. **Tryb online** - GPU jest po stronie serwera, nie lokalnie
2. **Ollama nie widzi GPU** - brak CUDA/cuDNN
3. **Ollama używa CPU** - domyślnie może używać CPU
4. **Model nie jest uruchomiony** - Ollama nie działa
5. **Ollama nie jest skonfigurowane do użycia GPU** - brak zmiennej środowiskowej

## Jak sprawdzić:

### 1. Sprawdź który tryb jest aktywny:
```python
print(f"LLM mode: {generator.llm_mode}")
print(f"LLM type: {type(generator.llm)}")
```

### 2. Sprawdź czy Ollama używa GPU:
```bash
# Windows PowerShell
ollama ps

# Lub sprawdź logi Ollama podczas uruchamiania
# Powinieneś zobaczyć: "GPU: NVIDIA GeForce..." lub podobne
```

### 3. Wymuś użycie GPU w Ollama (Windows PowerShell):

**ROZWIĄZANIE: Użyj bezpośredniego API Ollama (tak jak `ollama run`)**

```powershell
# W pliku .env ustaw:
OLLAMA_USE_DIRECT_API=true

# Lub w PowerShell przed uruchomieniem:
$env:OLLAMA_USE_DIRECT_API="true"

# Uruchom Ollama (jeśli nie działa)
ollama serve

# Teraz Python użyje tego samego API co 'ollama run' - GPU będzie używane!
```

**Dlaczego to działa:**
- `ollama run` używa bezpośredniego API (`/api/chat`) - to wymusza GPU
- `ChatOllama` z LangChain może używać innego endpointu - może nie wymuszać GPU
- Bezpośrednie API = ten sam endpoint co `ollama run` = GPU działa!

### 4. Sprawdź czy wywołania LLM są wykonywane:
**DEBUG printy zostały dodane!** Teraz zobaczysz:
```
[DEBUG] Process 1 (fill_tokens): Calling LLM (mode: online, type: ChatOpenAI)
[DEBUG] Process 1: LLM response received
[DEBUG] Process 2 (morphology): Calling LLM (mode: online, type: ChatOpenAI)
[DEBUG] Process 2: LLM response received
```

### 5. Sprawdź czy GPU jest używane (Windows):
```powershell
# Sprawdź użycie GPU przez Ollama
Get-Process ollama | Select-Object ProcessName, Id

# Lub użyj nvidia-smi (jeśli masz NVIDIA GPU)
nvidia-smi
```

## WAŻNE: Dla trybu ONLINE (PLLuM API):
- **GPU jest po stronie serwera** - nie zobaczysz użycia GPU lokalnie
- Lokalnie tylko HTTP request/response
- GPU używa serwer PLLuM API

## WAŻNE: Dla trybu LOCAL (Ollama):
- **GPU musi być skonfigurowane w Ollama** przed uruchomieniem
- `ChatOllama` w Pythonie NIE kontroluje GPU - to robi serwer Ollama
- Musisz ustawić `OLLAMA_NUM_GPU=1` PRZED uruchomieniem `ollama serve`

