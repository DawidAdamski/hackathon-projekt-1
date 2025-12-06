"""Prompty dla LLM - uzupełnianie tokenów i korekta morfologii."""

FILL_TOKENS_SYSTEM = """Jesteś ekspertem od generowania syntetycznych danych osobowych w języku polskim.
Twoim zadaniem jest uzupełnienie brakujących tokenów w tekście.

FORMAT ODPOWIEDZI:
Zwróć TYLKO czysty tekst z podmienionymi tokenami. NIE dodawaj żadnych formatów, komentarzy ani wyjaśnień.

PRZYKŁAD DOBREJ ODPOWIEDZI:
Wejście: "Nazywam się [name] [surname], mieszkam w [city]."
Wyjście: "Nazywam się Jan Kowalski, mieszkam w Warszawie."

PRZYKŁADY ZŁYCH ODPOWIEDZI (NIE RÓB TEGO):
❌ "Oto poprawiony tekst: Nazywam się Jan Kowalski..."
❌ {"filled": "Nazywam się Jan Kowalski..."}
❌ [{'text': 'Nazywam się Jan Kowalski...'}]
❌ "Nazywam się Jan Kowalski... Explanation: ..."

KRYTYCZNE ZASADY:
- Zwróć TYLKO tekst z podmienionymi tokenami
- BEZ komentarzy, BEZ wyjaśnień, BEZ nagłówków
- BEZ formatów JSON, BEZ list, BEZ słowa "explanation"
- ZACHOWAJ wulgaryzmy jeśli są w tekście
- Zachowaj resztę tekstu BEZ ZMIAN"""

FILL_TOKENS_PROMPT = """W tekście są tokeny w nawiasach kwadratowych (np. [name], [city], [address]).
Podmień KAŻDY token na realistyczne polskie dane.

MAPOWANIE TOKENÓW:
- [name] → Jan, Anna, Krzysztof, Maria, Piotr
- [surname] → Kowalski, Nowak, Wiśniewski, Zieliński
- [city] → Warszawa, Kraków, Gdańsk, Wrocław
- [address] → ul. Długa 15, 00-001 Warszawa
- [phone] → +48 123 456 789 lub 123 456 789
- [email] → jan.kowalski@email.pl
- [pesel] → 90010112345
- [age] → 35
- [sex] → mężczyzna lub kobieta

PRZYKŁADY (wejście → wyjście):

Przykład 1:
Wejście: "Nazywam się [name] [surname], mam [age] lat."
Wyjście: "Nazywam się Anna Kowalska, mam 35 lat."

Przykład 2:
Wejście: "Mieszkam w [city] przy [address]. Kontakt: [email]"
Wyjście: "Mieszkam w Warszawie przy ul. Długa 15, 00-001 Warszawa. Kontakt: anna.kowalska@email.pl"

Przykład 3:
Wejście: "Telefon: [phone], PESEL: [pesel]"
Wyjście: "Telefon: +48 123 456 789, PESEL: 90010112345"

FORMAT ODPOWIEDZI:
Zwróć TYLKO tekst z podmienionymi tokenami. BEZ formatów JSON, BEZ list, BEZ komentarzy.

OPTYMALIZACJA:
Jeśli tekst NIE MA żadnych tokenów do uzupełnienia (wszystkie tokeny już zostały zastąpione), 
zwróć TYLKO: TEKST_JEST_TAKI_SAM
To oszczędza tokeny - nie przepisuj całego tekstu jeśli nie ma zmian!

Tekst do uzupełnienia:
{text}

Odpowiedź (TYLKO tekst z tokenami lub "TEKST_JEST_TAKI_SAM"):"""


MORPHOLOGY_SYSTEM = """Jesteś ekspertem od języka polskiego.
Twoim zadaniem jest poprawienie morfologii tekstu - przypadków, form czasowników, zgodności rodzaju.

FORMAT ODPOWIEDZI:
Zwróć TYLKO czysty tekst z poprawioną morfologią. NIE dodawaj żadnych formatów, komentarzy ani wyjaśnień.

PRZYKŁAD DOBREJ ODPOWIEDZI:
Wejście: "Róża prosił o pomoc. Mieszkam w Warszawa."
Wyjście: "Róża prosiła o pomoc. Mieszkam w Warszawie."

PRZYKŁADY ZŁYCH ODPOWIEDZI (NIE RÓB TEGO):
❌ "Oto poprawiony tekst: Róża prosiła o pomoc..."
❌ {"corrected": "Róża prosiła o pomoc..."}
❌ [{'text': 'Róża', 'corrected': 'Róża'}, {'text': 'prosił', 'corrected': 'prosiła'}]
❌ "Róża prosiła o pomoc. Explanation: poprawiono formę czasownika..."
❌ "Róża prosiła o pomoc.```"
❌ Zwracanie tylko fragmentu tekstu zamiast CAŁEGO tekstu

KRYTYCZNE ZASADY:
- NIE zmieniaj danych (imion, nazwisk, miast, numerów telefonów, emaili)
- Poprawiaj TYLKO formy gramatyczne
- BEZ formatów JSON, BEZ list, BEZ słowa "explanation"
- ZACHOWAJ wulgaryzmy jeśli są w tekście
- Zwróć TYLKO poprawiony tekst, BEZ komentarzy"""

MORPHOLOGY_PROMPT = """Sprawdź i popraw morfologię poniższego tekstu.

ZASADY POPRAWIANIA:
- Jeśli imię jest żeńskie (np. Anna, Maria, Róża), czasowniki powinny być w formie żeńskiej
- Jeśli imię jest męskie (np. Jan, Piotr, Adam, Oliwier), czasowniki powinny być w formie męskiej
- Jeśli jest sprzeczność między imieniem a płcią (np. "Oliwier, kobieta"), popraw płć na zgodną z imieniem (np. "Oliwier, mężczyzna")
- Popraw przypadki gramatyczne (np. "w Warszawa" → "w Warszawie")
- NIE zmieniaj samych danych (imion, nazwisk, miast, numerów) - tylko formy gramatyczne i sprzeczności płci

PRZYKŁADY POPRAWEK (wejście → wyjście):

Przykład 1:
Wejście: "Róża prosił o pomoc."
Wyjście: "Róża prosiła o pomoc."

Przykład 2:
Wejście: "Jan napisała list."
Wyjście: "Jan napisał list."

Przykład 3:
Wejście: "Oliwier, kobieta, ma 29 lat."
Wyjście: "Oliwier, mężczyzna, ma 29 lat."

Przykład 4:
Wejście: "Mieszkam w Warszawa przy ul. Długa."
Wyjście: "Mieszkam w Warszawie przy ul. Długiej."

Przykład 5:
Wejście: "Dane Jana Kowalski są poprawne."
Wyjście: "Dane Jana Kowalskiego są poprawne."

FORMAT ODPOWIEDZI:
Zwróć TYLKO tekst z poprawioną morfologią. BEZ formatów JSON, BEZ list, BEZ komentarzy, BEZ "Oto poprawiony tekst:", BEZ markdown code blocks (```).

OPTYMALIZACJA:
Jeśli tekst NIE WYMAGA żadnych poprawek morfologicznych (wszystko jest poprawne), 
zwróć TYLKO: TEKST_JEST_TAKI_SAM
To oszczędza tokeny - nie przepisuj całego tekstu jeśli nie ma zmian!

Tekst do korekty:
{text}

Odpowiedź (TYLKO tekst z poprawkami lub "TEKST_JEST_TAKI_SAM"):"""

