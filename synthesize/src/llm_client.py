"""
LLM Client - prosty wrapper DSPy (wzorzec z TestDspy).

Konfiguracja jest maksymalnie prosta:
    lm = dspy.LM(model="ollama/PRIHLOP/PLLuM:latest")
    dspy.configure(lm=lm)
    
Dla modelu online:
    init_llm(use_online=True)  # używa zmiennych środowiskowych
"""

import os
import dspy
from typing import Optional
from .prompts import (
    FILL_TOKENS_SYSTEM,
    FILL_TOKENS_PROMPT,
    MORPHOLOGY_SYSTEM,
    MORPHOLOGY_PROMPT,
)

# Globalna zmienna na model
_lm: Optional[dspy.LM] = None


def init_llm(
    model: Optional[str] = None,
    use_online: bool = False,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model_name: Optional[str] = None,
) -> dspy.LM:
    """
    Inicjalizacja LLM - prosta konfiguracja jak w TestDspy.
    
    Args:
        model: Nazwa modelu (dla trybu local, np. "ollama/PRIHLOP/PLLuM:latest")
        use_online: Jeśli True, używa modelu online zamiast lokalnego Ollama
        api_key: API key dla modelu online (jeśli None, pobiera z PLLUM_API_KEY)
        base_url: Base URL dla API (jeśli None, używa domyślnego)
        model_name: Nazwa modelu online (jeśli None, używa domyślnego)
    
    Returns:
        Skonfigurowany model DSPy
    """
    global _lm
    
    if use_online:
        # Tryb online - PLLuM API
        api_key = api_key or os.getenv("PLLUM_API_KEY")
        base_url = base_url or os.getenv(
            "PLLUM_BASE_URL",
            "https://apim-pllum-tst-pcn.azure-api.net/vllm/v1"
        )
        model_name = model_name or os.getenv(
            "PLLUM_MODEL_NAME",
            "CYFRAGOVPL/pllum-12b-nc-chat-250715"
        )
        
        if not api_key:
            raise ValueError(
                "PLLUM_API_KEY not set. Set it as environment variable or pass as api_key parameter."
            )
        
        # Ustaw nagłówek dla LiteLLM (PLLuM API wymaga Ocp-Apim-Subscription-Key)
        # Musimy ustawić to PRZED utworzeniem dspy.LM, bo DSPy używa LiteLLM wewnętrznie
        try:
            import litellm
            # os jest już zaimportowane na górze pliku
            
            # Metoda 1: Ustaw globalne nagłówki dla LiteLLM - to jest główna metoda
            # LiteLLM użyje tych nagłówków dla wszystkich wywołań OpenAI-compatible
            # WAŻNE: litellm.headers dodaje nagłówki, ale NIE nadpisuje Authorization
            # Musimy usunąć Authorization i użyć tylko Ocp-Apim-Subscription-Key
            litellm.headers = {
                "Ocp-Apim-Subscription-Key": api_key,
                # NIE dodajemy Authorization - PLLuM API nie używa Bearer token
            }
            
            # Metoda 2: Ustaw również OPENAI_API_KEY jako backup (wymagane przez LiteLLM)
            # Ale nie będzie używane jako Authorization, bo mamy litellm.headers
            os.environ["OPENAI_API_KEY"] = api_key  # Wymagane przez LiteLLM do inicjalizacji
            
            # Metoda 3: Wyłącz verbose (można włączyć dla debugowania)
            litellm.set_verbose = False
            
        except ImportError:
            pass  # litellm może nie być dostępne, ale DSPy powinno działać
        
        # Utwórz model OpenAI-compatible
        openai_model = f"openai/{model_name}" if not model_name.startswith("openai/") else model_name
        
        # Utwórz DSPy LM - DSPy używa LiteLLM wewnętrznie
        # Przekazujemy api_key (wymagane przez LiteLLM), ale litellm.headers nadpisze Authorization
        # Nagłówek Ocp-Apim-Subscription-Key jest już ustawiony w litellm.headers
        # Próbujemy również przekazać extra_headers przez kwargs (jeśli DSPy/LiteLLM to obsługuje)
        _lm = dspy.LM(
            model=openai_model,
            api_key=api_key,  # Wymagane przez LiteLLM do inicjalizacji klienta
            api_base=base_url,
            # litellm.headers nadpisze Authorization: Bearer na Ocp-Apim-Subscription-Key
            # Próbujemy również przekazać extra_headers (jeśli DSPy/LiteLLM to obsługuje)
            extra_headers={"Ocp-Apim-Subscription-Key": api_key},  # Backup - przez kwargs
        )
        
        # Sprawdź czy nagłówki są ustawione (dla debugowania)
        try:
            import litellm
            if hasattr(litellm, 'headers') and litellm.headers:
                print(f"  Headers: {list(litellm.headers.keys())}")
                # Sprawdź również, czy nagłówki są faktycznie ustawione
                if "Ocp-Apim-Subscription-Key" in litellm.headers:
                    print(f"  ✓ Ocp-Apim-Subscription-Key header set")
        except:
            pass
        
        dspy.configure(lm=_lm)
        print(f"✓ LLM initialized (online): {model_name}")
        print(f"  API: {base_url}")
        return _lm
    else:
        # Tryb local - Ollama
        model = model or "ollama/PRIHLOP/PLLuM:latest"
        _lm = dspy.LM(model=model)
        dspy.configure(lm=_lm)
        print(f"✓ LLM initialized (local): {model}")
        return _lm


def get_lm() -> Optional[dspy.LM]:
    """Pobierz aktualny model LLM."""
    return _lm


def is_initialized() -> bool:
    """Sprawdź czy LLM jest zainicjalizowany."""
    return _lm is not None


# --- DSPy Signatures ---

class FillTokensSignature(dspy.Signature):
    """Uzupełnij brakujące tokeny [...] w tekście syntetycznymi danymi."""
    text: str = dspy.InputField(desc="Tekst z tokenami w nawiasach kwadratowych do uzupełnienia")
    filled: str = dspy.OutputField(desc="Tekst z uzupełnionymi tokenami - TYLKO tekst, bez komentarzy")


class CorrectMorphologySignature(dspy.Signature):
    """Popraw morfologię tekstu (przypadki, formy czasowników, zgodność rodzaju)."""
    text: str = dspy.InputField(desc="Tekst do korekty morfologicznej")
    corrected: str = dspy.OutputField(desc="Tekst z poprawioną morfologią - TYLKO tekst, bez komentarzy")


# --- Moduły DSPy ---

# Lazy initialization - moduły tworzone przy pierwszym użyciu
_fill_module: Optional[dspy.Predict] = None
_morph_module: Optional[dspy.Predict] = None


def _get_fill_module() -> dspy.Predict:
    """Lazy init dla modułu fill."""
    global _fill_module
    if _fill_module is None:
        _fill_module = dspy.Predict(FillTokensSignature)
    return _fill_module


def _get_morph_module() -> dspy.Predict:
    """Lazy init dla modułu morphology."""
    global _morph_module
    if _morph_module is None:
        _morph_module = dspy.Predict(CorrectMorphologySignature)
    return _morph_module


def fill_tokens(text: str) -> str:
    """
    Faza 2: Uzupełnij brakujące tokeny [...] używając LLM.
    
    Args:
        text: Tekst z tokenami do uzupełnienia
        
    Returns:
        Tekst z uzupełnionymi tokenami
    """
    if not is_initialized():
        raise RuntimeError("LLM not initialized. Call init_llm() first.")
    
    try:
        module = _get_fill_module()
        result = module(text=text)
        
        # DSPy może zwrócić różne formaty - obsłuż wszystkie
        filled_text = None
        
        # 1. Sprawdź atrybuty obiektu
        if hasattr(result, 'filled'):
            filled_text = result.filled
        elif hasattr(result, 'output'):
            filled_text = result.output
        # 2. Sprawdź dict (LLM czasem zwraca JSON z "-filled")
        elif isinstance(result, dict):
            filled_text = (
                result.get('filled') or 
                result.get('-filled') or 
                result.get('text') or 
                result.get('output') or
                result.get('result')
            )
        # 3. Sprawdź string
        elif isinstance(result, str):
            filled_text = result
        # 4. Sprawdź czy to obiekt z __dict__
        elif hasattr(result, '__dict__'):
            filled_text = result.__dict__.get('filled') or result.__dict__.get('-filled')
        
        # 5. Jeśli nadal brak, spróbuj wyciągnąć z surowej odpowiedzi
        if not filled_text:
            filled_text = str(result)
            # Jeśli to JSON string, spróbuj sparsować
            if filled_text.strip().startswith('{'):
                try:
                    import json
                    json_data = json.loads(filled_text)
                    filled_text = (
                        json_data.get('filled') or 
                        json_data.get('-filled') or 
                        json_data.get('text') or 
                        json_data.get('output')
                    ) or filled_text
                except:
                    pass
        
        # Jeśli nadal nie mamy tekstu, użyj oryginalnego tekstu
        cleaned = _clean_response(filled_text) if filled_text else text
        
        # OPTYMALIZACJA: Sprawdź czy LLM zwrócił klucz "TEKST_JEST_TAKI_SAM"
        if cleaned.strip().upper() == "TEKST_JEST_TAKI_SAM":
            # Tekst nie wymaga zmian - zwróć oryginalny
            return text
        
        # Fallback: jeśli wyczyszczony tekst jest znacznie krótszy niż oryginalny (podejrzane obcięcie)
        if len(cleaned) < len(text) * 0.1 and len(cleaned) < 50:
            print(f"⚠️ LLM returned suspiciously short text ({len(cleaned)} chars), using original")
            return text
        
        return cleaned
    except Exception as e:
        print(f"⚠️ LLM fill_tokens error: {e}")
        # Spróbuj użyć prompt mode jako fallback
        try:
            return fill_tokens_with_prompt(text)
        except:
            return text  # Zwróć oryginalny tekst w przypadku błędu


def correct_morphology(text: str) -> str:
    """
    Faza 3: Popraw morfologię tekstu używając LLM.
    
    Args:
        text: Tekst do korekty
        
    Returns:
        Tekst z poprawioną morfologią
    """
    if not is_initialized():
        raise RuntimeError("LLM not initialized. Call init_llm() first.")
    
    try:
        module = _get_morph_module()
        result = module(text=text)
        
        # DSPy może zwrócić różne formaty - obsłuż wszystkie
        corrected_text = None
        
        # 1. Sprawdź atrybuty obiektu
        if hasattr(result, 'corrected'):
            corrected_text = result.corrected
        elif hasattr(result, 'output'):
            corrected_text = result.output
        # 2. Sprawdź dict (LLM czasem zwraca JSON z "-corrected")
        elif isinstance(result, dict):
            corrected_text = (
                result.get('corrected') or 
                result.get('-corrected') or 
                result.get('text') or 
                result.get('output') or
                result.get('result')
            )
        # 3. Sprawdź string
        elif isinstance(result, str):
            corrected_text = result
        # 4. Sprawdź czy to obiekt z __dict__
        elif hasattr(result, '__dict__'):
            corrected_text = result.__dict__.get('corrected') or result.__dict__.get('-corrected')
        
        # 5. Jeśli nadal brak, spróbuj wyciągnąć z surowej odpowiedzi
        if not corrected_text:
            corrected_text = str(result)
            # Jeśli to JSON string, spróbuj sparsować
            if corrected_text.strip().startswith('{'):
                try:
                    import json
                    json_data = json.loads(corrected_text)
                    corrected_text = (
                        json_data.get('corrected') or 
                        json_data.get('-corrected') or 
                        json_data.get('text') or 
                        json_data.get('output')
                    ) or corrected_text
                except:
                    pass
        
        # Jeśli nadal nie mamy tekstu, użyj oryginalnego tekstu
        if not corrected_text:
            print(f"⚠️ LLM returned empty response, using original")
            return text
        
        cleaned = _clean_response(corrected_text)
        
        # ZABEZPIECZENIE 0: Sprawdź czy LLM zwrócił analizę morfologiczną zamiast tekstu
        # Przykład: {'text': [{'form': '...', 'comment': '...'}]}
        if cleaned.strip().startswith("{'text':") or cleaned.strip().startswith('{"text":'):
            # Sprawdź czy to lista z 'form' i 'comment' - to jest analiza morfologiczna, nie tekst!
            import re
            if re.search(r"'form'|'comment'|\"comment\"", cleaned):
                print(f"⚠️ LLM returned morphological analysis instead of text. Using original.")
                return text
        
        # OPTYMALIZACJA: Sprawdź czy LLM zwrócił klucz "TEKST_JEST_TAKI_SAM"
        if cleaned.strip().upper() == "TEKST_JEST_TAKI_SAM":
            # Tekst nie wymaga zmian - zwróć oryginalny
            return text
        
        # ZABEZPIECZENIE 1: Sprawdź czy tekst nie został przepisany na inny język
        # Jeśli tekst zawiera dużo angielskich słów, prawdopodobnie LLM zmienił język
        import re
        english_words = re.findall(r'\b(the|and|or|but|in|on|at|to|for|of|with|by|a|an|is|are|was|were|be|been|being|have|has|had|do|does|did|will|would|could|should|may|might|must|can|says|say|said|here|help|let|go|over|your|situation|step|mentioned|that|you|live|phone|number|email|great|know|this|information|now|discuss|job|warehouse|seems|like|boss|constantly|nagging|mother|bothered|small|things|home|definitely|frustrating|stressful|however|try|remember|these|are|normal|challenges|life|most|people|through|them|as|for|sleep|problems|perfectly|fine|feel|concerned|instead|diagnosing|yourself|depression|why|not|schedule|appointment|doctor|therapist|they|can|provide|professional|advice|support|meantime|develop|healthy|habits|regular|exercise|meditation|consistent|bedtime|routine|reduce|stress|improve|quality|finally|don|afraid|ask|when|need|it|there|many|resources|available|including|online|support|groups|hotlines|hang|there|other|questions|concerns)\b', cleaned.lower())
        if len(english_words) > 5:  # Jeśli jest więcej niż 5 angielskich słów, prawdopodobnie to błąd
            print(f"⚠️ LLM changed language to English (detected {len(english_words)} English words). Using original text.")
            return text
        
        # ZABEZPIECZENIE 2: Sprawdź czy tekst nie został drastycznie zmieniony
        # Jeśli długość różni się o więcej niż 50%, prawdopodobnie LLM dodał komentarze/analizy
        if len(text) > 100:  # Tylko dla dłuższych tekstów
            length_diff = abs(len(cleaned) - len(text)) / len(text)
            if length_diff > 0.5:  # Różnica większa niż 50%
                print(f"⚠️ LLM response length differs significantly ({len(cleaned)} vs {len(text)}, diff: {length_diff:.1%}). Using original.")
                return text
        
        # ZABEZPIECZENIE 3: Sprawdź czy tekst zaczyna się od angielskich fraz (np. "A woman's voice says:")
        english_prefixes = [
            r'^A\s+\w+\'?s?\s+voice\s+says?:',
            r'^Here\s+is\s+the',
            r'^Let\s+me\s+',
            r'^I\s+can\s+see',
            r'^Great\s+to\s+know',
        ]
        for pattern in english_prefixes:
            if re.search(pattern, cleaned, re.IGNORECASE):
                print(f"⚠️ LLM added English commentary. Using original text.")
                return text
        
        # Fallback: jeśli wyczyszczony tekst jest znacznie krótszy niż oryginalny (podejrzane obcięcie)
        # Ale tylko jeśli oryginalny tekst był dłuższy niż 50 znaków (żeby nie blokować krótkich odpowiedzi)
        if len(text) > 50 and len(cleaned) < len(text) * 0.1 and len(cleaned) < 50:
            print(f"⚠️ LLM returned suspiciously short text ({len(cleaned)} chars, original: {len(text)}), using original")
            return text
        
        return cleaned
    except Exception as e:
        print(f"⚠️ LLM correct_morphology error: {e}")
        # Spróbuj użyć prompt mode jako fallback
        try:
            return correct_morphology_with_prompt(text)
        except:
            return text  # Zwróć oryginalny tekst w przypadku błędu


def _clean_response(response: str) -> str:
    """
    Wyczyść odpowiedź LLM z niepotrzebnych elementów.
    
    Usuwa formaty JSON, markdown, ale ZACHOWUJE wulgaryzmy.
    
    Args:
        response: Surowa odpowiedź LLM
        
    Returns:
        Wyczyszczony tekst
    """
    if not response:
        return ""
    
    import re
    import json
    
    text = str(response).strip()
    
    # 1. Spróbuj parsować jako pełny JSON najpierw (najbardziej niezawodne)
    try:
        if text.strip().startswith('{') or text.strip().startswith('['):
            json_data = json.loads(text)
            
            # ZABEZPIECZENIE: Sprawdź czy to analiza morfologiczna (np. {'text': [{'form': '...', 'comment': '...'}]})
            if isinstance(json_data, dict) and 'text' in json_data:
                if isinstance(json_data['text'], list) and len(json_data['text']) > 0:
                    if isinstance(json_data['text'][0], dict) and ('form' in json_data['text'][0] or 'comment' in json_data['text'][0]):
                        # To jest analiza morfologiczna - zwróć pusty string, żeby funkcja wywołująca mogła użyć oryginalnego tekstu
                        return ""
            
            # Szukaj wartości w różnych możliwych kluczach
            for key in ['filled', '-filled', 'corrected', '-corrected', 'text', 'output', 'result']:
                if key in json_data:
                    extracted = json_data[key]
                    # Sprawdź czy to nie jest lista z analizą morfologiczną
                    if isinstance(extracted, list) and len(extracted) > 0:
                        if isinstance(extracted[0], dict) and ('form' in extracted[0] or 'comment' in extracted[0]):
                            # To jest analiza morfologiczna
                            return ""
                    text = str(extracted)
                    break
            # Jeśli to lista, weź pierwszy element
            if isinstance(json_data, list) and len(json_data) > 0:
                if isinstance(json_data[0], dict):
                    # Sprawdź czy to nie jest analiza morfologiczna
                    if 'form' in json_data[0] or 'comment' in json_data[0]:
                        return ""
                    for key in ['text', 'content', 'output', 'filled', 'corrected']:
                        if key in json_data[0]:
                            text = str(json_data[0][key])
                            break
                else:
                    text = str(json_data[0])
    except (json.JSONDecodeError, KeyError, IndexError, TypeError):
        pass  # Nie jest JSON, kontynuuj normalne czyszczenie
    
    # 2. Usuń formaty typu {corrected} na początku (bez cudzysłowów)
    # Przykład: "{corrected} Tekst..." → "Tekst..."
    # Ale tylko jeśli to jest na samym początku tekstu
    if text.strip().startswith('{corrected}'):
        text = re.sub(r'^\{corrected\}\s*', '', text, flags=re.IGNORECASE | re.MULTILINE)
    if text.strip().startswith('{filled}'):
        text = re.sub(r'^\{filled\}\s*', '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    # 3. Spróbuj wyciągnąć JSON z regex (dla niepełnych JSON)
    # Obsługuj różne formaty: {"key": "value"}, {key: "value"}, {'key': 'value'}
    json_patterns = [
        r'\{["\']?-filled["\']?\s*:\s*["\']([^"\']+)["\']\s*\}',  # {"-filled": "..."}
        r'\{["\']?filled["\']?\s*:\s*["\']([^"\']+)["\']\s*\}',   # {"filled": "..."}
        r'\{["\']?-corrected["\']?\s*:\s*["\']([^"\']+)["\']\s*\}',  # {"-corrected": "..."}
        r'\{["\']?corrected["\']?\s*:\s*["\']([^"\']+)["\']\s*\}',   # {"corrected": "..."}
        r'\{["\']?text["\']?\s*:\s*["\']([^"\']+)["\']\s*\}',       # {"text": "..."}
        r'\{["\']?output["\']?\s*:\s*["\']([^"\']+)["\']\s*\}',    # {"output": "..."}
        r'\{corrected\s*:\s*["\']([^"\']+)["\']\s*\}',              # {corrected: "..."}
        r'\{filled\s*:\s*["\']([^"\']+)["\']\s*\}',                # {filled: "..."}
    ]
    for pattern in json_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            text = match.group(1)
            break
    
    # 4. Usuń formaty typu [{'text': '...', 'corrected': '...'}] lub [{"text": "...", "corrected": "..."}]
    # Spróbuj najpierw sparsować jako JSON listę (z podwójnymi cudzysłowami)
    try:
        if text.strip().startswith('['):
            # Najpierw spróbuj json.loads (dla formatu z podwójnymi cudzysłowami)
            json_list = json.loads(text)
            if isinstance(json_list, list) and len(json_list) > 0:
                # Jeśli to lista słowników z kluczem 'corrected', zbierz wszystkie 'corrected'
                if isinstance(json_list[0], dict):
                    corrected_parts = []
                    for item in json_list:
                        if 'corrected' in item:
                            corrected_parts.append(str(item['corrected']))
                        elif 'text' in item:
                            corrected_parts.append(str(item['text']))
                    if corrected_parts:
                        text = ' '.join(corrected_parts)
                        # Nie kontynuuj dalej, już mamy tekst
                        return ' '.join(text.split()).strip()
    except (json.JSONDecodeError, KeyError, IndexError, TypeError):
        # Jeśli json.loads nie zadziałał, spróbuj ast.literal_eval (dla formatu z pojedynczymi cudzysłowami)
        try:
            import ast
            if text.strip().startswith('['):
                parsed_list = ast.literal_eval(text)
                if isinstance(parsed_list, list) and len(parsed_list) > 0:
                    if isinstance(parsed_list[0], dict):
                        corrected_parts = []
                        for item in parsed_list:
                            if isinstance(item, dict):
                                if 'corrected' in item:
                                    corrected_parts.append(str(item['corrected']))
                                elif 'text' in item:
                                    corrected_parts.append(str(item['text']))
                        if corrected_parts:
                            text = ' '.join(corrected_parts)
                            # Nie kontynuuj dalej, już mamy tekst
                            return ' '.join(text.split()).strip()
        except (ValueError, SyntaxError, TypeError):
            pass  # Nie jest lista Python, kontynuuj normalne czyszczenie
    
    # Regex fallback dla formatów listowych
    list_pattern = r'\[\s*\{["\']?text["\']?\s*:\s*["\']([^"\']+)["\']\s*\}\s*\]'
    match = re.search(list_pattern, text, re.IGNORECASE)
    if match:
        text = match.group(1)
    
    # 5. Usuń pozostałe JSON-y w środku tekstu (jeśli LLM dodał JSON w środku)
    # Przykład: "Tekst... [ { "text": "...", "corrected": "..." } ]"
    # Usuń całe bloki JSON w nawiasach kwadratowych
    text = re.sub(r'\s*\[\s*\{[^}]+\}\s*\]\s*', ' ', text, flags=re.IGNORECASE | re.DOTALL)
    # Usuń również pojedyncze obiekty JSON w nawiasach klamrowych (jeśli nie są na początku)
    # Ale tylko jeśli są w środku tekstu, nie na początku
    if not text.strip().startswith('{'):
        text = re.sub(r'\s*\{[^}]*"corrected"[^}]*\}\s*', ' ', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*\{[^}]*"text"[^}]*\}\s*', ' ', text, flags=re.IGNORECASE | re.DOTALL)
    
    # 6. Usuń markdown formatting (ale zachowaj wulgaryzmy!)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic*
    text = re.sub(r'__([^_]+)__', r'\1', text)      # __bold__
    text = re.sub(r'_([^_]+)_', r'\1', text)        # _italic_
    
    # 6. Usuń typowe prefiksy LLM (ale NIE usuwa wulgaryzmów)
    # Usuń tylko na początku tekstu - UWAGA: nie usuwaj jeśli to jedyne słowo w tekście!
    # NIE usuwaj "Cześć!" ani "Hej!" jeśli tekst jest krótki - to może być część oryginalnego tekstu!
    original_length = len(text)
    original_text = text  # Backup
    
    # Bezpieczne prefiksy (tylko te które NIGDY nie są częścią oryginalnego tekstu)
    safe_prefixes = [
        r'^Oto poprawiony tekst[:\s]+',
        r'^Oto[:\s]+',
        r'^Poprawiona wersja[:\s]+',
        r'^Poprawiony tekst[:\s]+',
        r'^Tekst[:\s]+',
        r'^Odpowiedź[:\s]+',
        r'^Explanation[:\s]+',
        r'^Wyjaśnienie[:\s]+',
        r'^<[^>]*Output[^>]*>',  # < Output for the first text >
        r'^<[^>]*output[^>]*>',  # < output for... >
    ]
    
    for pattern in safe_prefixes:
        new_text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
        # Jeśli usunięcie nie spowodowało drastycznego skrócenia, zastosuj
        if len(new_text) >= original_length * 0.8 or original_length < 20:
            text = new_text
        # Jeśli spowodowało, nie rób nic (zachowaj oryginalny tekst)
    
    # "Hej!" i "Cześć!" - usuń TYLKO jeśli tekst jest długi (prawdopodobnie dodane przez LLM)
    # Jeśli tekst jest krótki, to może być część oryginalnego tekstu!
    if original_length > 50:  # Tylko dla długich tekstów
        text = re.sub(r'^Hej![:\s]+', '', text, flags=re.IGNORECASE | re.MULTILINE)
        text = re.sub(r'^Cześć![:\s]+', '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    # Usuń również prefiksy w środku tekstu jeśli są po kropce lub myślniku
    text = re.sub(r'\.\s+Oto poprawiony tekst[:\s]+', '. ', text, flags=re.IGNORECASE)
    text = re.sub(r'\.\s+Oto[:\s]+', '. ', text, flags=re.IGNORECASE)
    text = re.sub(r'-\s+Oto poprawiony tekst[:\s]+', '- ', text, flags=re.IGNORECASE)
    text = re.sub(r'-\s+Oto[:\s]+', '- ', text, flags=re.IGNORECASE)
    
    # 7. Usuń "explanation:" lub "wyjaśnienie:" w środku tekstu (ale zachowaj resztę)
    text = re.sub(r'\s+explanation\s*:\s*', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+wyjaśnienie\s*:\s*', ' ', text, flags=re.IGNORECASE)
    
    # 8. Usuń sufixy typu "Explanation: ..." na końcu (całe zdanie po "Explanation:")
    text = re.sub(r'\s*Explanation\s*:.*$', '', text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    text = re.sub(r'\s*Wyjaśnienie\s*:.*$', '', text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    
    # 8a. Usuń komentarze w nawiasach trójkątnych (np. < Output for the first text >)
    text = re.sub(r'\s*<[^>]*Output[^>]*>\s*', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*<[^>]*output[^>]*>\s*', ' ', text, flags=re.IGNORECASE)
    # Usuń również na początku i końcu
    text = re.sub(r'^<[^>]*Output[^>]*>\s*', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'\s*<[^>]*Output[^>]*>$', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^<[^>]*output[^>]*>\s*', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'\s*<[^>]*output[^>]*>$', '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    # 8b. Usuń komentarze w nawiasach (np. "(nie ma takiego słowa jak \"PARku\")")
    # Ale tylko jeśli są na początku lub końcu linii, nie w środku tekstu
    text = re.sub(r'^\s*\([^)]*nie\s+ma[^)]*\)\s*', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'\s*\([^)]*nie\s+ma[^)]*\)\s*$', '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    # 9. Usuń markdown code blocks (``` na początku i końcu)
    text = re.sub(r'^```[a-z]*\s*', '', text, flags=re.MULTILINE)  # Usuń ``` na początku
    text = re.sub(r'\s*```\s*$', '', text, flags=re.MULTILINE)  # Usuń ``` na końcu
    text = re.sub(r'```', '', text)  # Usuń wszystkie pozostałe ```
    
    # 10. Normalizuj białe znaki (ale zachowaj wulgaryzmy!)
    # UWAGA: Nie używaj ' '.join(text.split()) jeśli tekst jest pusty lub bardzo krótki
    # To może obciąć tekst jeśli są tylko białe znaki
    if text.strip():
        text = ' '.join(text.split())
    
    return text.strip()


# --- Alternatywne wywołanie z promptami ---

def fill_tokens_with_prompt(text: str) -> str:
    """
    Alternatywna wersja fill_tokens używająca pełnych promptów.
    Użyj gdy dspy.Predict nie daje dobrych wyników.
    """
    if not is_initialized():
        raise RuntimeError("LLM not initialized. Call init_llm() first.")
    
    prompt = FILL_TOKENS_PROMPT.format(text=text)
    
    try:
        # Bezpośrednie wywołanie LM
        response = _lm(prompt)
        if isinstance(response, list) and len(response) > 0:
            return _clean_response(response[0])
        return _clean_response(str(response))
    except Exception as e:
        print(f"⚠️ LLM fill_tokens_with_prompt error: {e}")
        return text


def correct_morphology_with_prompt(text: str) -> str:
    """
    Alternatywna wersja correct_morphology używająca pełnych promptów.
    Użyj gdy dspy.Predict nie daje dobrych wyników.
    """
    if not is_initialized():
        raise RuntimeError("LLM not initialized. Call init_llm() first.")
    
    prompt = MORPHOLOGY_PROMPT.format(text=text)
    
    try:
        # Bezpośrednie wywołanie LM
        response = _lm(prompt)
        if isinstance(response, list) and len(response) > 0:
            return _clean_response(response[0])
        return _clean_response(str(response))
    except Exception as e:
        print(f"⚠️ LLM correct_morphology_with_prompt error: {e}")
        return text

