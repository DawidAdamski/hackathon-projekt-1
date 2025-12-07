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

KRYTYCZNE ZASADY - PRZECZYTAJ UWAŻNIE:
1. NIE ZMIENIAJ JĘZYKA - tekst MUSI pozostać w języku polskim
2. NIE PRZEPISUJ tekstu - zwróć TEN SAM tekst, tylko z poprawioną morfologią
3. NIE DODAWAJ analiz, komentarzy, wyjaśnień, porad
4. NIE ZMIENIAJ treści - tylko formy gramatyczne
5. ZACHOWAJ wszystkie słowa, zdania, strukturę tekstu
6. Poprawiaj TYLKO: przypadki, formy czasowników, zgodność rodzaju

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
❌ "A woman's voice says: ..." (NIE ZMIENIAJ JĘZYKA NA ANGIELSKI!)
❌ Dodawanie analiz psychologicznych, porad, komentarzy
❌ Przepisywanie tekstu na inny język
❌ Zwracanie tylko fragmentu tekstu zamiast CAŁEGO tekstu

KRYTYCZNE ZASADY:
- NIE zmieniaj języka tekstu (musi pozostać polski)
- NIE zmieniaj danych (imion, nazwisk, miast, numerów telefonów, emaili)
- NIE dodawaj analiz, porad, komentarzy
- Poprawiaj TYLKO formy gramatyczne (przypadki, formy czasowników, zgodność rodzaju)
- BEZ formatów JSON, BEZ list, BEZ słowa "explanation"
- ZACHOWAJ wulgaryzmy jeśli są w tekście
- Zwróć TYLKO poprawiony tekst, BEZ komentarzy"""

MORPHOLOGY_PROMPT = """Sprawdź i popraw morfologię poniższego tekstu.

KRYTYCZNE ZASADY - PRZECZYTAJ UWAŻNIE:
1. NIE ZMIENIAJ JĘZYKA - tekst MUSI pozostać w języku polskim
2. NIE PRZEPISUJ tekstu - zwróć TEN SAM tekst, tylko z poprawioną morfologią
3. NIE DODAWAJ analiz, komentarzy, porad, wyjaśnień (np. "A woman's voice says:", "Let me help you", "< Output for... >", "(nie ma takiego słowa...)")
4. NIE ZMIENIAJ treści - tylko formy gramatyczne
5. ZACHOWAJ wszystkie słowa, zdania, strukturę tekstu
6. NIE ZMIENIAJ nazw własnych, skrótów technicznych, kodów (np. "PARKU" → NIE zmieniaj na "PUSZCZY", "MG_LOP_P501_00G" → NIE zmieniaj)
7. NIE poprawiaj rzeczy, które są poprawne (np. "PARKU" jest poprawne - NIE zmieniaj!)

ZASADY POPRAWIANIA:
- Jeśli imię jest żeńskie (np. Anna, Maria, Róża), czasowniki powinny być w formie żeńskiej
- Jeśli imię jest męskie (np. Jan, Piotr, Adam, Oliwier, Konrad, Ryszard), czasowniki powinny być w formie męskiej
- Jeśli jest sprzeczność między imieniem a płcią (np. "Konrad, kobieta"), popraw płć na zgodną z imieniem (np. "Konrad, mężczyzna")
- Popraw przypadki gramatyczne (np. "w Warszawa" → "w Warszawie")
- NIE zmieniaj samych danych (imion, nazwisk, miast, numerów) - tylko formy gramatyczne i sprzeczności płci
- ZACHOWAJ wulgaryzmy jeśli są w tekście - NIE usuwaj ich, NIE zamieniaj na "możesz odejść"
- NIE analizuj składni - TYLKO popraw morfologię
- NIE dodawaj analiz psychologicznych, porad, komentarzy
- NIE zmieniaj nazw własnych, skrótów technicznych, kodów, oznaczeń (np. "PARKU KRAJOBRAZOWEGO" → NIE zmieniaj na "PUSZCZY")
- NIE poprawiaj rzeczy, które są już poprawne - tylko rzeczywiste błędy morfologiczne

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

Przykład 6:
Wejście: "Konrad, 67 lat, kobieta. Mieszkam w Wyszków."
Wyjście: "Konrad, 67 lat, mężczyzna. Mieszkam w Wyszkowie."

Przykład 7:
Wejście: "Jak się sprzeciwiam, mówi 'No Ryszard, jak ci się nie podoba, to wypierdalaj'."
Wyjście: "Jak się sprzeciwiam, mówi 'No Konrad, jak ci się nie podoba, to wypierdalaj'."
(NIE zmieniaj "wypierdalaj" na "możesz odejść" - zachowaj wulgaryzm!)

Przykład 4:
Wejście: "Mieszkam w Warszawa przy ul. Długa."
Wyjście: "Mieszkam w Warszawie przy ul. Długiej."

Przykład 5:
Wejście: "Dane Jana Kowalski są poprawne."
Wyjście: "Dane Jana Kowalskiego są poprawne."

FORMAT ODPOWIEDZI:
Zwróć TYLKO tekst z poprawioną morfologią. BEZ formatów JSON, BEZ list, BEZ komentarzy, BEZ "Oto poprawiony tekst:", BEZ markdown code blocks (```).
KRYTYCZNE: NIE zwracaj analizy morfologicznej (np. {'text': [{'form': '...', 'comment': '...'}]}) - zwróć TYLKO poprawiony tekst!

OPTYMALIZACJA:
Jeśli tekst NIE WYMAGA żadnych poprawek morfologicznych (wszystko jest poprawne), 
zwróć TYLKO: TEKST_JEST_TAKI_SAM
To oszczędza tokeny - nie przepisuj całego tekstu jeśli nie ma zmian!

Tekst do korekty:
{text}

Odpowiedź (TYLKO tekst z poprawkami lub "TEKST_JEST_TAKI_SAM"):"""

