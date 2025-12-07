"""
Faker Processor - Faza 1 przetwarzania.

Szybkie zastępowanie tokenów [...] syntetycznymi danymi z Fakera.
Nie wymaga LLM - deterministyczne i szybkie.
"""

import re
from typing import Callable, Dict
from faker import Faker

# Inicjalizacja Fakera z polskim locale
fake = Faker('pl_PL')
Faker.seed(None)  # Random seed dla różnorodności


# Mapowanie tokenów na generatory Fakera
TOKEN_GENERATORS: Dict[str, Callable[[], str]] = {
    # Dane osobowe
    "name": lambda: fake.first_name(),
    "surname": lambda: fake.last_name(),
    "first_name": lambda: fake.first_name(),
    "last_name": lambda: fake.last_name(),
    
    # Lokalizacja
    "city": lambda: fake.city(),
    # Adres - TYLKO ulica z numerem (bez kodu pocztowego i miasta, bo miasto jest osobno)
    "address": lambda: fake.street_address(),  # Zwraca np. "ul. Długa 15" bez kodu i miasta
    "street": lambda: fake.street_name(),
    
    # Kontakt
    "phone": lambda: fake.phone_number(),
    "email": lambda: fake.email(),
    "username": lambda: fake.user_name(),
    "user-name": lambda: fake.user_name(),
    
    # Dokumenty
    "pesel": lambda: fake.numerify("###########"),
    "document-number": lambda: fake.bothify("???######").upper(),
    "document_number": lambda: fake.bothify("???######").upper(),  # Alias
    "id-number": lambda: fake.bothify("???######").upper(),  # Alias dla ID number
    "id_number": lambda: fake.bothify("???######").upper(),  # Alias
    "nip": lambda: fake.numerify("###-###-##-##"),
    "regon": lambda: fake.numerify("#########"),
    
    # Finanse
    "bank-account": lambda: fake.numerify("## #### #### #### #### #### ####"),
    "bank_account": lambda: fake.numerify("## #### #### #### #### #### ####"),  # Alias
    "iban": lambda: "PL" + fake.numerify("## #### #### #### #### #### ####"),
    "credit-card": lambda: fake.credit_card_number(),
    "credit-card-number": lambda: fake.credit_card_number(),  # Zgodnie z dokumentem
    "credit_card_number": lambda: fake.credit_card_number(),  # Alias
    
    # Inne
    "age": lambda: str(fake.random_int(18, 80)),
    "sex": lambda: fake.random_element(["mężczyzna", "kobieta"]),
    "company": lambda: fake.company(),
    "date": lambda: fake.date(),
    "data": lambda: fake.date(),  # Alias
    "date-of-birth": lambda: fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%d.%m.%Y"),
    "date_of_birth": lambda: fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%d.%m.%Y"),  # Alias
    "job": lambda: fake.job(),
    "job-title": lambda: fake.job(),  # Alias dla job-title
    "job_title": lambda: fake.job(),  # Alias z podkreślnikiem
    "school-name": lambda: fake.random_element([
        "Szkoła Podstawowa", "Liceum Ogólnokształcące", "Technikum",
        "Szkoła Zawodowa", "Gimnazjum", "Szkoła Średnia"
    ]) + " nr " + str(fake.random_int(1, 50)),
    "school_name": lambda: fake.random_element([
        "Szkoła Podstawowa", "Liceum Ogólnokształcące", "Technikum",
        "Szkoła Zawodowa", "Gimnazjum", "Szkoła Średnia"
    ]) + " nr " + str(fake.random_int(1, 50)),  # Alias
    
    # Wrażliwe
    "political-view": lambda: fake.random_element([
        "centrowe", "umiarkowane", "liberalne", "konserwatywne"
    ]),
    "political_view": lambda: fake.random_element([
        "centrowe", "umiarkowane", "liberalne", "konserwatywne"
    ]),  # Alias z podkreślnikiem
    "health": lambda: fake.random_element([
        "dobry stan zdrowia", "wymaga kontroli", "pod opieką lekarza"
    ]),
    "relative": lambda: fake.random_element([
        "brat", "siostra", "matka", "ojciec", "syn", "córka", "małżonek/ka"
    ]),
    "ethnicity": lambda: fake.random_element([
        "Polak", "Polka", "Niemiec", "Niemka", "Ukrainiec", "Ukrainka",
        "Białorusin", "Białorusinka", "Rosjanin", "Rosjanka"
    ]),
    "religion": lambda: fake.random_element([
        "katolik", "katoliczka", "protestant", "protestantka",
        "prawosławny", "prawosławna", "ateista", "ateistka"
    ]),
    "sexual-orientation": lambda: fake.random_element([
        "heteroseksualna", "homoseksualna", "biseksualna"
    ]),
    "sexual_orientation": lambda: fake.random_element([
        "heteroseksualna", "homoseksualna", "biseksualna"
    ]),  # Alias
    "secret": lambda: fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
}


def process_with_faker(text: str) -> str:
    """
    Faza 1: Zastąp tokeny [...] wartościami z Fakera.
    
    Szybkie przetwarzanie bez LLM. Obsługuje większość typowych tokenów.
    
    Args:
        text: Tekst z tokenami w nawiasach kwadratowych
        
    Returns:
        Tekst z zastąpionymi tokenami (niektóre mogą pozostać jeśli nieznane)
    
    Example:
        >>> process_with_faker("Nazywam się [name] [surname].")
        "Nazywam się Jan Kowalski."
    """
    def replace_token(match: re.Match) -> str:
        token = match.group(1).lower().strip()
        generator = TOKEN_GENERATORS.get(token)
        
        if generator:
            return generator()
        else:
            # Nieznany token - pozostaw bez zmian (LLM uzupełni w Fazie 2)
            return match.group(0)
    
    # Regex dla tokenów: [cokolwiek]
    pattern = r'\[([^\]]+)\]'
    return re.sub(pattern, replace_token, text)


def has_remaining_tokens(text: str) -> bool:
    """
    Sprawdź czy w tekście są jeszcze tokeny [...].
    
    Używane do optymalizacji - Faza 2 (LLM fill) jest pomijana
    jeśli nie ma pozostałych tokenów.
    
    Args:
        text: Tekst do sprawdzenia
        
    Returns:
        True jeśli są tokeny do uzupełnienia, False w przeciwnym razie
    """
    pattern = r'\[([^\]]+)\]'
    return bool(re.search(pattern, text))


def extract_tokens(text: str) -> list[str]:
    """
    Wyodrębnij wszystkie tokeny z tekstu.
    
    Args:
        text: Tekst do analizy
        
    Returns:
        Lista tokenów (bez nawiasów kwadratowych)
    
    Example:
        >>> extract_tokens("Jestem [name] z [city].")
        ['name', 'city']
    """
    pattern = r'\[([^\]]+)\]'
    return re.findall(pattern, text)


def count_tokens(text: str) -> dict[str, int]:
    """
    Policz wystąpienia każdego typu tokenu.
    
    Args:
        text: Tekst do analizy
        
    Returns:
        Słownik {token: liczba_wystąpień}
    
    Example:
        >>> count_tokens("[name] i [name] z [city]")
        {'name': 2, 'city': 1}
    """
    from collections import Counter
    tokens = extract_tokens(text)
    return dict(Counter(tokens))


def get_supported_tokens() -> list[str]:
    """
    Zwróć listę obsługiwanych tokenów.
    
    Returns:
        Lista nazw tokenów obsługiwanych przez Fakera
    """
    return list(TOKEN_GENERATORS.keys())

