"""
Morphological generator for Polish language.
Uses Faker to generate synthetic data and Spacy to preserve morphological forms.
Optionally uses LLM for more context-aware generation.
"""

import os
import re
from typing import Optional, Dict, Any
import spacy
from faker import Faker

# Optional LLM imports
try:
    from langchain_openai import ChatOpenAI
    from dotenv import load_dotenv
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# Optional Ollama imports
try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# For direct Ollama API calls (to force GPU usage)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class MorphologicalGenerator:
    """
    Generates synthetic Polish data with morphological awareness.
    
    Uses Spacy to analyze morphological features (case, number, gender)
    and attempts to preserve them when generating replacements.
    """
    
    def __init__(
        self,
        locale: str = "pl_PL",
        spacy_model: str = "pl_core_news_lg",
        use_llm: Optional[bool] = None,
        use_morphology: bool = True,
        llm_mode: Optional[str] = None
    ):
        """
        Initialize the morphological generator.
        
        Args:
            locale: Faker locale (default: "pl_PL")
            spacy_model: Spacy model name for Polish (default: "pl_core_news_lg")
            use_llm: Whether to use LLM for generation (None = auto-detect from env)
            use_morphology: Whether to use Spacy for morphological analysis (default: True)
                           Set to False for simple faking without morphology preservation
            llm_mode: LLM mode - "online" (PLLuM API) or "local" (Ollama). 
                     If None, reads from config.yaml or env
        """
        self.faker = Faker(locale)
        self.locale = locale
        self.use_morphology = use_morphology
        
        # Load environment variables and config
        if LLM_AVAILABLE or OLLAMA_AVAILABLE:
            load_dotenv()
        
        # Load config.yaml if available
        self.config = self._load_config()
        
        # Load prompts.yaml if available
        self.prompts = self._load_prompts()
        
        # Determine LLM mode
        if llm_mode is None:
            llm_mode = self.config.get("llm", {}).get("mode", "online")
            if llm_mode is None:
                llm_mode = os.getenv("LLM_MODE", "online")
        
        # Initialize LLM if available and requested
        self.llm = None
        self.llm_mode = llm_mode
        if use_llm is None:
            use_llm = os.getenv("USE_LLM_FOR_SYNTHESIS", "false").lower() == "true"
        
        if use_llm:
            if llm_mode == "local" and OLLAMA_AVAILABLE:
                self._init_ollama()
            elif llm_mode == "online" and LLM_AVAILABLE:
                self._init_llm()
            elif use_llm and not (LLM_AVAILABLE or OLLAMA_AVAILABLE):
                print("Warning: LLM requested but langchain-openai or langchain-ollama not installed. Using Faker only.")
        
        # Initialize Spacy only if morphology is enabled
        self.nlp = None
        if use_morphology:
            try:
                self.nlp = spacy.load(spacy_model)
            except OSError:
                # Fallback to smaller model if large model not available
                try:
                    self.nlp = spacy.load("pl_core_news_md")
                except OSError:
                    print(f"Warning: Spacy model '{spacy_model}' not found. Continuing without morphology.")
                    print("  Install with: python -m spacy download pl_core_news_lg")
                    self.nlp = None
                    self.use_morphology = False
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.yaml if available."""
        from pathlib import Path
        config_path = Path(__file__).parent.parent.parent / "config.yaml"
        if config_path.exists():
            try:
                import yaml
                with open(config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Could not load config.yaml: {e}")
        return {}
    
    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts from prompts.yaml if available, fallback to config.yaml."""
        from pathlib import Path
        prompts_path = Path(__file__).parent.parent.parent / "prompts.yaml"
        if prompts_path.exists():
            try:
                import yaml
                with open(prompts_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Could not load prompts.yaml: {e}")
        
        # Fallback to config.yaml if prompts.yaml doesn't exist
        if self.config.get("prompts"):
            return self.config.get("prompts", {})
        
        return {}
    
    def _init_llm(self):
        """Initialize online LLM client (PLLuM API) from config or environment variables."""
        # Get config or use defaults
        llm_config = self.config.get("llm", {}).get("online", {})
        
        api_key = os.getenv("PLLUM_API_KEY")
        base_url = os.getenv("PLLUM_BASE_URL") or llm_config.get("base_url", "https://apim-pllum-tst-pcn.azure-api.net/vllm/v1")
        model_name = os.getenv("PLLUM_MODEL_NAME") or llm_config.get("model_name", "CYFRAGOVPL/pllum-12b-nc-chat-250715")
        temperature = float(os.getenv("PLLUM_TEMPERATURE") or llm_config.get("temperature", "0.7"))
        max_tokens = int(os.getenv("PLLUM_MAX_TOKENS") or llm_config.get("max_tokens", "300"))
        
        if not api_key or api_key == "your_api_key_here":
            print("Warning: PLLUM_API_KEY not set. LLM generation disabled.")
            return
        
        try:
            self.llm = ChatOpenAI(
                model=model_name,
                openai_api_key="EMPTY",  # Required but not used
                openai_api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
                default_headers={
                    'Ocp-Apim-Subscription-Key': api_key
                }
            )
            print(f"✓ LLM initialized (online mode: {model_name})")
        except Exception as e:
            print(f"Warning: Failed to initialize LLM: {e}. Using Faker only.")
            self.llm = None
    
    def _init_ollama(self):
        """Initialize local LLM client (Ollama) from config or environment variables."""
        # Get config or use defaults
        llm_config = self.config.get("llm", {}).get("local", {})
        
        base_url = os.getenv("OLLAMA_BASE_URL") or llm_config.get("base_url", "http://localhost:11434")
        model_name = os.getenv("OLLAMA_MODEL_NAME") or llm_config.get("model_name", "PRIHLOP/PLLuM:latest")
        temperature = float(os.getenv("OLLAMA_TEMPERATURE") or llm_config.get("temperature", "0.7"))
        max_tokens = int(os.getenv("OLLAMA_MAX_TOKENS") or llm_config.get("max_tokens", "300"))
        
        # Check if we should use direct API (for GPU forcing) or ChatOllama
        use_direct_api = os.getenv("OLLAMA_USE_DIRECT_API", "false").lower() == "true"
        
        if use_direct_api and REQUESTS_AVAILABLE:
            # Use direct Ollama API to force GPU usage
            print(f"  Using direct Ollama API (GPU forced)")
            self.llm = {
                "type": "direct_api",
                "base_url": base_url,
                "model": model_name,
                "temperature": temperature,
                "num_predict": max_tokens,
            }
            print(f"✓ LLM initialized (local mode, direct API: {model_name})")
            print(f"  Direct API mode forces GPU usage via Ollama server")
        elif OLLAMA_AVAILABLE:
            # Use ChatOllama (standard LangChain way)
            try:
                # Build model_kwargs for additional Ollama options
                # According to LangChain docs: https://docs.langchain.com/oss/python/integrations/chat/ollama
                # ChatOllama passes options to Ollama API via model_kwargs
                model_kwargs = {}
                
                # Check if we should force GPU layers (if specified in env)
                num_gpu = os.getenv("OLLAMA_NUM_GPU")
                if num_gpu:
                    try:
                        model_kwargs["num_gpu"] = int(num_gpu)
                        print(f"  GPU layers configured: {num_gpu}")
                    except ValueError:
                        pass
                
                # Create ChatOllama instance
                # Note: According to LangChain docs, Ollama automatically optimizes GPU usage
                # but we can pass additional options via model_kwargs
                self.llm = ChatOllama(
                    model=model_name,
                    base_url=base_url,
                    temperature=temperature,
                    num_predict=max_tokens,
                    model_kwargs=model_kwargs if model_kwargs else None,
                )
                print(f"✓ LLM initialized (local mode: {model_name})")
                print(f"  Note: Ollama automatically optimizes GPU usage if available")
                print(f"  To force GPU layers: set OLLAMA_NUM_GPU=<number> in environment")
                print(f"  To use direct API (like 'ollama run'): set OLLAMA_USE_DIRECT_API=true")
            except Exception as e:
                print(f"Warning: Failed to initialize ChatOllama: {e}")
                if REQUESTS_AVAILABLE:
                    print(f"  Falling back to direct API...")
                    self.llm = {
                        "type": "direct_api",
                        "base_url": base_url,
                        "model": model_name,
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    }
                    print(f"✓ LLM initialized (local mode, direct API fallback: {model_name})")
                else:
                    print("  Install langchain-ollama or requests for Ollama support")
                    self.llm = None
        else:
            if REQUESTS_AVAILABLE:
                print(f"  langchain-ollama not available, using direct API")
                self.llm = {
                    "type": "direct_api",
                    "base_url": base_url,
                    "model": model_name,
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
                print(f"✓ LLM initialized (local mode, direct API: {model_name})")
            else:
                print("Warning: Neither langchain-ollama nor requests available. Install one of them.")
                self.llm = None
    
    def _call_ollama_direct_api(self, user_prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """
        Call Ollama API directly (bypassing LangChain) to ensure GPU usage.
        This uses the same API endpoint that 'ollama run' uses.
        """
        if not REQUESTS_AVAILABLE:
            return None
        
        if not isinstance(self.llm, dict) or self.llm.get("type") != "direct_api":
            return None
        
        base_url = self.llm["base_url"]
        model = self.llm["model"]
        temperature = self.llm["temperature"]
        num_predict = self.llm["num_predict"]
        
        # Build messages for chat API
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        
        # Call Ollama chat API (same as 'ollama run' uses)
        url = f"{base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict,
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            
            # Extract message content
            if "message" in result and "content" in result["message"]:
                return result["message"]["content"].strip()
            return None
        except Exception as e:
            print(f"Warning: Direct Ollama API call failed: {e}")
            return None
    
    def _analyze_context_with_llm(self, text: str, token: str) -> Optional[str]:
        """
        Analyze context using LLM to determine if token is part of address, person name, etc.
        
        Args:
            text: Full text context around the token
            token: Token to analyze (e.g., "[name]", "[city]")
            
        Returns:
            Suggested entity type or None if LLM not available
        """
        if not self.llm:
            return None
        
        # Get context analysis prompt from prompts.yaml or use default
        prompt_template = self.prompts.get("context_analysis_prompt", 
            """Przeanalizuj kontekst i określ, czy token "{token}" w poniższym tekście to:
- imię osoby (jeśli jest w kontekście osoby, np. "Inż [name] [surname]")
- część adresu (jeśli jest w kontekście adresu, np. "ulica [name]")
- nazwa miejscowości (jeśli jest w kontekście miejsca)

Tekst: {context}

Odpowiedz TYLKO jednym słowem: "osoba", "adres", "miejscowosc", lub "nieznane".""")
        
        prompt = prompt_template.format(token=token, context=text[:500])
        
        try:
            response = self.llm.invoke(prompt)
            
            # Extract result
            result = None
            if hasattr(response, 'json'):
                try:
                    json_data = response.json()
                    result = json_data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                except (AttributeError, KeyError, IndexError):
                    pass
            
            if not result and hasattr(response, 'content'):
                result = response.content.strip()
            
            if not result and isinstance(response, dict):
                result = response.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            
            if not result:
                result = str(response).strip()
            
            return result.lower() if result else None
        except Exception as e:
            print(f"Warning: LLM context analysis failed: {e}")
            return None
    
    def _fill_missing_tokens_with_llm(self, text: str) -> Optional[str]:
        """
        Process 1: Fill missing tokens (e.g., [name], [city]) that Faker didn't replace.
        WARUNKOWY - wykonywany tylko jeśli są tokeny w nawiasach kwadratowych.
        
        Args:
            text: Text with potentially remaining tokens in square brackets
            
        Returns:
            Text with all tokens replaced, or None if LLM not available or no tokens found
        """
        if not self.llm:
            return None
        
        # Check if there are any tokens to replace - WARUNKOWY proces
        import re
        if not re.search(r'\[([^\]]+)\]', text):
            return None  # No tokens to replace - skip this process
        
        # Debug: log LLM call for Process 1 (fill tokens) - only if tokens found
        llm_type = "direct_api" if isinstance(self.llm, dict) else type(self.llm).__name__
        print(f"[DEBUG] Process 1 (fill_tokens): Calling LLM (mode: {self.llm_mode}, type: {llm_type})")
        
        # Get prompt from prompts.yaml
        fill_prompt_template = self.prompts.get("fill_tokens_prompt", 
            "W tekście są tokeny w nawiasach kwadratowych. Podmień je na odpowiednie dane syntetyczne.")
        
        system_prompt = self.prompts.get("system_prompt") or self.config.get("llm", {}).get("system_prompt")
        
        # Clear instruction: only return text, no comments
        user_prompt = f"{fill_prompt_template}\n\nTekst:\n{text}\n\nZwróć TYLKO poprawiony tekst, BEZ komentarzy."
        
        try:
            
            # Handle direct API call (for GPU forcing)
            if isinstance(self.llm, dict) and self.llm.get("type") == "direct_api":
                response_text = self._call_ollama_direct_api(user_prompt, system_prompt)
                if response_text:
                    print(f"[DEBUG] Process 1: LLM response received")
                    return self._clean_llm_response(response_text)
                return None
            
            # Handle ChatOllama or ChatOpenAI
            if system_prompt and hasattr(self.llm, 'invoke'):
                from langchain_core.messages import SystemMessage, HumanMessage
                messages = []
                if system_prompt:
                    messages.append(SystemMessage(content=system_prompt))
                messages.append(HumanMessage(content=user_prompt))
                response = self.llm.invoke(messages)
            else:
                response = self.llm.invoke(user_prompt)
            
            print(f"[DEBUG] Process 1: LLM response received")
            
            # Extract result
            result = None
            if hasattr(response, 'json'):
                try:
                    json_data = response.json()
                    result = json_data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                except (AttributeError, KeyError, IndexError):
                    pass
            
            if not result and hasattr(response, 'content'):
                result = response.content.strip()
            
            if not result and isinstance(response, dict):
                result = response.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            
            if not result:
                result = str(response).strip()
            
            # Clean up: remove formatting, newlines, and any comments/headers
            if result:
                # Remove markdown formatting (**, __, etc.)
                result = re.sub(r'\*\*([^*]+)\*\*', r'\1', result)  # Remove **bold**
                result = re.sub(r'__([^_]+)__', r'\1', result)  # Remove __bold__
                result = re.sub(r'\*([^*]+)\*', r'\1', result)  # Remove *italic*
                result = re.sub(r'_([^_]+)_', r'\1', result)  # Remove _italic_
                
                # Remove newlines and normalize spaces
                result = ' '.join(result.split())
                
                # Remove common comment patterns that LLM might add (at the end)
                comment_patterns = [
                    r'W tekście wprowadzono.*$',
                    r'Wprowadzono następujące zmiany.*$',
                    r'Zmiany:.*$',
                    r'Token.*zastąpiono.*$',
                    r'^Oto poprawiony tekst[:\s]*',
                    r'^Poprawiona wersja[:\s]*',
                    r'^Oto tekst[:\s]*',
                    r'^Tekst poprawiony[:\s]*',
                    r'^Poprawiony tekst[:\s]*',
                    r'^Odpowiedź[:\s]*',
                ]
                for pattern in comment_patterns:
                    result = re.sub(pattern, '', result, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
                
                result = result.strip()
            
            return result if result else None
        except Exception as e:
            print(f"Warning: LLM token filling failed: {e}")
            return None
    
    def _correct_morphology_with_llm(self, text: str) -> Optional[str]:
        """
        Process 2: Correct morphology (grammatical case, number, gender) of generated data.
        ZAWSZE wykonywany - sprawdza morfologię i poprawia z minimalną zmianą.
        
        Args:
            text: Text with synthetic data (already without tokens)
            
        Returns:
            Text with corrected morphology, or None if LLM not available
        """
        if not self.llm:
            return None
        
        # Get prompt from prompts.yaml
        morph_prompt_template = self.prompts.get("morphology_correction_prompt",
            "Sprawdź i popraw morfologię (przypadek, liczba, rodzaj) danych w tekście. Minimalne zmiany.")
        
        system_prompt = self.prompts.get("system_prompt") or self.config.get("llm", {}).get("system_prompt")
        
        # Clear instruction: only return text, no comments, minimal changes, don't regenerate data
        user_prompt = f"{morph_prompt_template}\n\nTekst:\n{text}\n\nZwróć TYLKO poprawiony tekst, BEZ komentarzy. NIE generuj nowych danych - poprawiaj TYLKO formy gramatyczne."
        
        try:
            # Debug: log LLM call for Process 2 (morphology)
            llm_type = "direct_api" if isinstance(self.llm, dict) else type(self.llm).__name__
            print(f"[DEBUG] Process 2 (morphology): Calling LLM (mode: {self.llm_mode}, type: {llm_type})")
            
            # Handle direct API call (for GPU forcing)
            if isinstance(self.llm, dict) and self.llm.get("type") == "direct_api":
                response_text = self._call_ollama_direct_api(user_prompt, system_prompt)
                if response_text:
                    print(f"[DEBUG] Process 2: LLM response received")
                    return self._clean_llm_response(response_text)
                return None
            
            # Handle ChatOllama or ChatOpenAI
            if system_prompt and hasattr(self.llm, 'invoke'):
                from langchain_core.messages import SystemMessage, HumanMessage
                messages = []
                if system_prompt:
                    messages.append(SystemMessage(content=system_prompt))
                messages.append(HumanMessage(content=user_prompt))
                response = self.llm.invoke(messages)
            else:
                response = self.llm.invoke(user_prompt)
            
            print(f"[DEBUG] Process 2: LLM response received")
            
            # Extract result
            result = None
            if hasattr(response, 'json'):
                try:
                    json_data = response.json()
                    result = json_data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                except (AttributeError, KeyError, IndexError):
                    pass
            
            if not result and hasattr(response, 'content'):
                result = response.content.strip()
            
            if not result and isinstance(response, dict):
                result = response.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            
            if not result:
                result = str(response).strip()
            
            # Clean up: remove formatting, newlines, and any comments/headers
            if result:
                # Remove markdown formatting (**, __, etc.)
                result = re.sub(r'\*\*([^*]+)\*\*', r'\1', result)  # Remove **bold**
                result = re.sub(r'__([^_]+)__', r'\1', result)  # Remove __bold__
                result = re.sub(r'\*([^*]+)\*', r'\1', result)  # Remove *italic*
                result = re.sub(r'_([^_]+)_', r'\1', result)  # Remove _italic_
                
                # Remove newlines and normalize spaces
                result = ' '.join(result.split())
                
                # Remove common comment patterns that LLM might add (at the end)
                comment_patterns = [
                    r'W tekście wprowadzono.*$',
                    r'Wprowadzono następujące zmiany.*$',
                    r'Zmiany:.*$',
                    r'^Oto poprawiony tekst[:\s]*',
                    r'^Poprawiona wersja[:\s]*',
                    r'^Oto tekst[:\s]*',
                    r'^Tekst poprawiony[:\s]*',
                    r'^Poprawiony tekst[:\s]*',
                    r'^Odpowiedź[:\s]*',
                ]
                for pattern in comment_patterns:
                    result = re.sub(pattern, '', result, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
                
                result = result.strip()
            
            return result if result else None
        except Exception as e:
            print(f"Warning: LLM morphology correction failed: {e}")
            return None
    
    def _generate_with_llm(
        self,
        original_text: str,
        entity_type: str,
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate synthetic data using LLM.
        
        Args:
            original_text: Original text to replace
            entity_type: Entity type (e.g., "{name}", "{city}")
            context: Optional context from surrounding text
            
        Returns:
            Generated text or None if LLM is not available
        """
        if not self.llm:
            return None
        
        # Get system prompt from prompts.yaml or config.yaml
        system_prompt = self.prompts.get("system_prompt") or self.config.get("llm", {}).get("system_prompt")
        
        # Get entity prompts from prompts.yaml or use defaults
        entity_prompts = self.prompts.get("entity_prompts", {})
        default_prompt_template = self.prompts.get("default_prompt", "Wygeneruj polskie dane typu {entity_type}.")
        
        user_prompt = entity_prompts.get(entity_type)
        if not user_prompt:
            # Use default prompt template if entity type not found
            user_prompt = default_prompt_template.format(entity_type=entity_type)
        
        if context:
            # Add context information - that Faker already generated data
            user_prompt = f"Kontekst (tekst z wstępnie wygenerowanymi danymi przez Faker): {context}\n\n{user_prompt}"
        
        try:
            # Use system prompt if available (for ChatOpenAI/ChatOllama)
            if system_prompt and hasattr(self.llm, 'invoke'):
                # Try to use system message if supported
                from langchain_core.messages import SystemMessage, HumanMessage
                messages = []
                if system_prompt:
                    messages.append(SystemMessage(content=system_prompt))
                messages.append(HumanMessage(content=user_prompt))
                response = self.llm.invoke(messages)
            else:
                # Fallback to simple prompt
                response = self.llm.invoke(user_prompt)
            
            # Handle different response formats
            result = None
            
            # Format 1: response.json()['choices'][0]['message']['content']
            if hasattr(response, 'json'):
                try:
                    json_data = response.json()
                    result = json_data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                except (AttributeError, KeyError, IndexError):
                    pass
            
            # Format 2: response.content (LangChain format)
            if not result and hasattr(response, 'content'):
                result = response.content.strip()
            
            # Format 3: Direct dict access
            if not result and isinstance(response, dict):
                result = response.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            
            # Format 4: String representation
            if not result:
                result = str(response).strip()
                # Try to extract JSON from string if it looks like JSON
                if result.startswith('{') or result.startswith('['):
                    try:
                        import json
                        json_data = json.loads(result)
                        result = json_data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                    except (json.JSONDecodeError, KeyError, IndexError):
                        pass
            
            return result if result else None
        except Exception as e:
            print(f"Warning: LLM generation failed: {e}. Falling back to Faker.")
            return None
    
    def _extract_morph_features(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract morphological features from text using Spacy.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with morphological features or None if analysis fails
        """
        if not self.use_morphology or not self.nlp:
            return None
        
        if not text or not text.strip():
            return None
        
        try:
            doc = self.nlp(text)
            if not doc:
                return None
            
            # Get first token (assuming single word or first word)
            first_token = doc[0] if len(doc) > 0 else None
            if not first_token:
                return None
            
            morph = first_token.morph
            
            features = {
                "case": None,
                "number": None,
                "gender": None,
                "pos": first_token.pos_,
            }
            
            # Extract case (przypadek)
            if "Case" in morph:
                features["case"] = str(morph.get("Case")[0]) if morph.get("Case") else None
            
            # Extract number (liczba)
            if "Number" in morph:
                features["number"] = str(morph.get("Number")[0]) if morph.get("Number") else None
            
            # Extract gender (rodzaj)
            if "Gender" in morph:
                features["gender"] = str(morph.get("Gender")[0]) if morph.get("Gender") else None
            
            return features
        except Exception as e:
            # If analysis fails, return None (will use simple replacement)
            return None
    
    def _simple_case_mapping(self, original: str, replacement: str, case: Optional[str]) -> str:
        """
        Simple case mapping for Polish nouns.
        This is a fallback when Spacy can't handle inflection.
        
        Args:
            original: Original word
            replacement: Replacement word
            case: Case from morphological analysis
            
        Returns:
            Replacement word (potentially modified)
        """
        # This is a simplified approach - in production, you'd use Morfeusz
        # For now, we return the replacement as-is
        # The proper solution would integrate with Morfeusz2 library
        
        # Simple heuristic: if original ends with certain suffixes, try to match
        if case:
            # Nominative (mianownik) - base form
            if case == "Nom":
                return replacement
            
            # Genitive (dopełniacz) - often ends with 'a' or 'u'
            if case == "Gen" and original.endswith(('a', 'u')):
                # Try to add similar ending (very simplified)
                if replacement.endswith(('a', 'e', 'o')):
                    return replacement
                # This is where Morfeusz would be needed for proper inflection
        
        return replacement
    
    def _is_male_name(self, name: str) -> bool:
        """
        Check if a Polish name is typically male.
        
        Args:
            name: Name to check
            
        Returns:
            True if name is typically male, False if female
        """
        name_lower = name.lower().strip()
        
        # Common Polish female name endings
        female_endings = ['a', 'ia', 'ka', 'na', 'la', 'ma', 'ra', 'sa', 'ta', 'wa', 'za']
        
        # Names ending with 'a' are usually female (except some like "Kuba", "Barnaba")
        # But most common pattern: if ends with 'a' and not in exceptions -> female
        if name_lower.endswith('a'):
            # Exceptions - male names ending with 'a'
            male_exceptions = ['kuba', 'barnaba', 'bonawentura', 'jarema', 'kosma']
            if name_lower in male_exceptions:
                return True
            return False
        
        # Names ending with consonants are usually male
        return True
    
    def generate_name(self, original_text: str, entity_type: str = "{name}") -> str:
        """
        Generate a synthetic first name, attempting to preserve morphology.
        Can also generate street names if entity_type is "{address}".
        
        Args:
            original_text: Original name text
            entity_type: Entity type (e.g., "{name}", "{surname}", "{address}")
            
        Returns:
            Synthetic name or street name
        """
        # If entity_type is address, generate street name instead
        if entity_type == "{address}":
            # Generate street name (Polish street names often end with specific suffixes)
            street_suffixes = ["a", "ego", "iego", "owa", "skiego"]
            base_name = self.faker.last_name()  # Use surname as base for street name
            suffix = self.faker.random.choice(street_suffixes)
            return f"{base_name}{suffix}"
        
        if entity_type == "{name}":
            synthetic = self.faker.first_name()
        elif entity_type == "{surname}":
            synthetic = self.faker.last_name()
        else:
            synthetic = self.faker.first_name()
        
        # Try to preserve case if morphology is enabled
        if self.use_morphology:
            morph_features = self._extract_morph_features(original_text)
            if morph_features and morph_features.get("case"):
                synthetic = self._simple_case_mapping(
                    original_text, synthetic, morph_features["case"]
                )
        
        return synthetic
    
    def generate_city(self, original_text: str) -> str:
        """
        Generate a synthetic city name.
        
        Args:
            original_text: Original city name
            
        Returns:
            Synthetic city name
        """
        synthetic = self.faker.city()
        
        # Try to preserve case if morphology is enabled
        if self.use_morphology:
            morph_features = self._extract_morph_features(original_text)
            if morph_features and morph_features.get("case"):
                synthetic = self._simple_case_mapping(
                    original_text, synthetic, morph_features["case"]
                )
        
        return synthetic
    
    def generate_address(self, original_text: str) -> str:
        """
        Generate a synthetic address.
        
        Args:
            original_text: Original address
            
        Returns:
            Synthetic address (single line, no newlines)
        """
        # faker.address() can return multi-line addresses, so we replace newlines with spaces
        address = self.faker.address()
        # Replace newlines and multiple spaces with single space
        address = ' '.join(address.split())
        return address
    
    def generate_phone(self, original_text: str) -> str:
        """
        Generate a synthetic phone number in Polish format.
        
        Args:
            original_text: Original phone number
            
        Returns:
            Synthetic phone number
        """
        # Polish phone format: +48 XXX XXX XXX or XXX XXX XXX
        return self.faker.phone_number()
    
    def generate_email(self, original_text: str) -> str:
        """
        Generate a synthetic email address.
        
        Args:
            original_text: Original email
            
        Returns:
            Synthetic email
        """
        return self.faker.email()
    
    def generate_username(self, original_text: str) -> str:
        """
        Generate a synthetic username.
        
        Args:
            original_text: Original username
            
        Returns:
            Synthetic username
        """
        # Generate username-like string (combination of name and numbers)
        name_part = self.faker.user_name()
        # Remove any special characters that might be in Faker's username
        name_part = ''.join(c for c in name_part if c.isalnum() or c in ['_', '-'])
        return name_part
    
    def generate_pesel(self, original_text: str) -> str:
        """
        Generate a synthetic PESEL number.
        
        Args:
            original_text: Original PESEL
            
        Returns:
            Synthetic PESEL (11 digits)
        """
        # PESEL is 11 digits, but we'll generate a random one
        # Note: This won't be a valid PESEL (would need checksum calculation)
        return self.faker.numerify("###########")
    
    def generate_document_number(self, original_text: str) -> str:
        """
        Generate a synthetic document number.
        
        Args:
            original_text: Original document number
            
        Returns:
            Synthetic document number
        """
        # Polish ID format: 3 letters + 6 digits (e.g., ABC123456)
        return self.faker.bothify("???######").upper()
    
    def generate_age(self, original_text: str) -> str:
        """
        Generate a synthetic age.
        
        Args:
            original_text: Original age
            
        Returns:
            Synthetic age (as string)
        """
        # Extract number from original if possible
        age_match = re.search(r'\d+', original_text)
        if age_match:
            # Generate similar age (within reasonable range)
            original_age = int(age_match.group())
            # Generate age within ±10 years, but keep it realistic (18-100)
            synthetic_age = max(18, min(100, original_age + self.faker.random_int(-10, 10)))
            return str(synthetic_age)
        
        return str(self.faker.random_int(18, 80))
    
    def generate_gender(self, original_text: str, context_name: Optional[str] = None) -> str:
        """
        Generate a synthetic gender.
        If context_name is provided, gender will match the name's typical gender.
        
        Args:
            original_text: Original gender text
            context_name: Optional name from context to determine gender consistency
            
        Returns:
            Synthetic gender ("mężczyzna" or "kobieta")
        """
        # If we have a name in context, use it to determine gender
        if context_name:
            is_male = self._is_male_name(context_name)
            return "mężczyzna" if is_male else "kobieta"
        
        # Otherwise randomly choose
        return self.faker.random.choice(["mężczyzna", "kobieta"])
    
    def generate_company(self, original_text: str) -> str:
        """
        Generate a synthetic company name.
        
        Args:
            original_text: Original company name
            
        Returns:
            Synthetic company name
        """
        return self.faker.company()
    
    def generate_date(self, original_text: str) -> str:
        """
        Generate a synthetic date.
        
        Args:
            original_text: Original date
            
        Returns:
            Synthetic date (formatted as string)
        """
        return self.faker.date()
    
    def generate_bank_account(self, original_text: str) -> str:
        """
        Generate a synthetic bank account number.
        
        Args:
            original_text: Original bank account
            
        Returns:
            Synthetic bank account (Polish format: 26 digits)
        """
        # Polish IBAN format: PL + 2 check digits + 24 account digits
        # Simplified: just generate numbers
        return self.faker.numerify("########################")
    
    def generate(
        self,
        original_text: str,
        entity_type: str,
        context: Optional[str] = None,
        prefer_llm: bool = False,
        context_values: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Main generation method that routes to appropriate generator based on entity type.
        Optionally uses LLM for more context-aware generation.
        
        Args:
            original_text: Original text to replace
            entity_type: Entity type (e.g., "{name}", "{city}", etc.)
            context: Optional context from surrounding text (for LLM)
            prefer_llm: If True, try LLM first (if available)
            
        Returns:
            Synthetic replacement text
        """
        entity_type = entity_type.lower()
        
        # Try LLM first if requested and available
        if prefer_llm and self.llm:
            llm_result = self._generate_with_llm(original_text, entity_type, context)
            if llm_result:
                # Clean up LLM result: strip and replace newlines with spaces
                llm_result = llm_result.strip()
                llm_result = ' '.join(llm_result.split())
                return llm_result
        
        # Fallback to Faker-based generators
        generators = {
            "{name}": self.generate_name,
            "{surname}": lambda x: self.generate_name(x, "{surname}"),
            "{city}": self.generate_city,
            "{address}": self.generate_address,
            "{phone}": self.generate_phone,
            "{email}": self.generate_email,
            "{pesel}": self.generate_pesel,
            "{document-number}": self.generate_document_number,
            "{age}": self.generate_age,
            "{sex}": lambda x: self.generate_gender(x, context_values.get("{name}") if context_values else None),
            "{company}": self.generate_company,
            "{date}": self.generate_date,
            "{data}": self.generate_date,
            "{bank-account}": self.generate_bank_account,
            "{username}": self.generate_username,
        }
        
        generator = generators.get(entity_type)
        if generator:
            result = generator(original_text)
            if result:
                # Clean up: strip whitespace and replace any newlines with spaces
                result = result.strip()
                # Replace any internal newlines/carriage returns with spaces
                result = ' '.join(result.split())
                # Store generated value in context for consistency
                if context_values is not None:
                    context_values[entity_type] = result
                return result
        
        # Fallback: if entity_type is unknown, try to generate something generic
        # Don't return [{entity_type}] as it creates confusion
        # Instead, return a simple placeholder or use Faker's random string
        return self.faker.word() if hasattr(self.faker, 'word') else f"[UNKNOWN:{entity_type}]"

