✅ 1/15 – PRAWDA W SIECI (fact-checking, dezinformacja)
Problem:

Szybkie szerzenie się dezinformacji w sieci; brak narzędzi do automatycznej weryfikacji treści.

Rozwiązanie:

Asystent AI analizujący artykuły / posty, wykrywający manipulacje, oceniający wiarygodność źródeł.

MVP:

Input: URL / tekst

Wykrycie: fałszywe tezy / emocjonalny język

Ocena źródeł

Krótki raport wiarygodności

Wykonalność: Wysoka

Prosty pipeline NLP + reguły + LLM.

✅ 2/15 – DANE BEZ TWARZY (anonimizacja danych)
Problem:

Urzędy i firmy udostępniają dane, ale nie mają narzędzi do skutecznej anonimizacji.

Rozwiązanie:

System wykrywający dane osobowe i automatycznie je zniekształcający.

MVP:

Upload pliku

Wykrywanie PII (NLP + regex)

Zastępowanie tokenami

Raport: co zostało zanonimizowane

Wykonalność: Wysoka

Gotowe biblioteki + LLM.

✅ 3/15 – WYSZUKIWARKA ANOMALII
Problem:

Systemy instytucji mają ogromne logi i dane — trudno znaleźć anomalie.

Rozwiązanie:

AI do wykrywania podejrzanych wzorców w danych tabelarycznych.

MVP:

Import CSV

Proste modele anomaly detection (Isolation Forest)

Lista wykrytych zdarzeń

Wizualizacja prostego wykresu

Wykonalność: Wysoka
✅ 4/15 – KONTROLA ZAKŁADÓW WZAJEMNYCH
Problem:

Nadzór państwa nad zakładami bukmacherskimi wymaga identyfikacji nieprawidłowości.

Rozwiązanie:

Model analizujący dane transakcyjne i wykrywający nielegalne wzorce.

MVP:

Załadowanie danych

Detekcja podejrzanych schematów (duże wygrane, częste zakłady, klony kont)

Raport + alerty

Wykonalność: Średnia (dane wymagają dobrego przygotowania)
✅ 5/15 – GAMING: LOS DECYDUJE
Problem:

Gracze nie ufają algorytmom RNG, brak przejrzystości losowań.

Rozwiązanie:

Publiczny, transparentny system generowania losowych wyników + walidacja.

MVP:

Publiczne API z seedem

Wizualizacja RNG

Generator wyników z możliwością weryfikacji

Wykonalność: Wysoka

Najprostszy projekt blockchain/RNG.

✅ 6/15 – ZGRANY BUDŻET (rozproszona edycja danych)

Źródło:

Problem:

Planowanie budżetu oparte na jednym Excelu → błędy, chaos, brak kontroli wersji.

Rozwiązanie:

Webowy system edycji danych dla wielu komórek + walidacja + scalanie.

MVP:

Edycja danych per komórka

Walidacja sum / braków

Automatyczne scalanie do jednego arkusza

Wykonalność: Wysoka
✅ 7/15 – INDEKS BRANŻ

Źródło:

Problem:

PKO BP potrzebuje narzędzia oceny kondycji branż.

Rozwiązanie:

Indeks sektorowy oparty na danych finansowych i alternatywnych.

MVP:

Pobranie danych (1–2 źródła)

Obliczenie kilku wskaźników (marża, wzrost, ryzyko)

Ranking branż + wykres

Wykonalność: Wysoka
✅ 8/15 – ZUS Accident Notification Tool (ZANT)

Źródło:

Problem:

Brak wsparcia dla zgłaszania wypadków + trudne decyzje o uznaniu zdarzenia.

Rozwiązanie:

Asystent + OCR + analiza przypadków + rekomendacja decyzji.

MVP:

Formularz zgłoszenia

OCR jednego PDF

Podstawowa rekomendacja (similarity search)

Wykonalność: Średnia
✅ 9/15 – AI w służbie decyzji (asystent orzecznika MSiT)

Źródło:

Problem:

Ogromne akta spraw → czasochłonne analizy + brak automatyzacji.

Rozwiązanie:

Asystent AI streszczający, analizujący i generujący propozycje decyzji.

MVP:

Upload dokumentu

Streszczenie + ekstrakcja faktów

Propozycja decyzji + uzasadnienie

Wykonalność: Wysoka
✅ 10/15 – CHMURA POD KONTROLĄ (CPK – klasyfikacja chmur punktów)

Źródło:

Problem:

Ogromne chmury punktów – ręczna klasyfikacja elementów infrastruktury.

Rozwiązanie:

Moduł ML klasyfikujący punkty (min. 5 klas).

MVP:

Wczytanie LAS

Prosta klasyfikacja (heurystyki / PointNet mini)

Eksport LAS z klasami

Wykonalność: Średnia–Niska (trudne ML)
✅ 11/15 – SCENARIUSZE JUTRA (MSZ)

Źródło:

Problem:

MSZ potrzebuje narzędzia do tworzenia scenariuszy geopolitycznych w oparciu o masę danych.

Rozwiązanie:

System analizujący fakty + generujący 4 scenariusze (12/36 mies., pozytywny/negatywny).

MVP:

Podsumowanie danych wejściowych

Scoring czynników

4 scenariusze + chain-of-thought

Wykonalność: Wysoka
✅ 12/15 – ZOBACZ TO, CZEGO NIE WIDAĆ (JSW ITS)

Źródło:

Problem:

Taśmy przenośników trzeba kontrolować ręcznie.

Rozwiązanie:

System CV mierzący szerokość taśmy + raporty + alerty.

MVP:

Detekcja taśmy (OpenCV / YOLOv8)

Pomiar szerokości

Raport CSV + API

Wykonalność: Wysoka
✅ 13/15 – BYDGOSZCZ – Ścieżki Pamięci 2.0

Źródło:

Problem:

Miejskie zabytki nie angażują odbiorców.

Rozwiązanie:

Interaktywna gra / AR / storytelling ożywiający pomniki.

MVP:

1 pomnik

Prosta scena AR / audio

Krótki quest/storyline

Wykonalność: Wysoka
✅ 14/15 – ODNALEZIONE ZGUBY (dane.gov.pl)

Źródło:

Problem:

Rejestry rzeczy znalezionych są rozproszone po BIP-ach.

Rozwiązanie:

“Jedno okno” do wgrywania danych przez urzędy w ≤5 krokach.

MVP:

Formularz + walidacja CSV

Podgląd danych

API push

Wzorcowy schemat danych

Wykonalność: Wysoka
✅ 15/15 – ŚCIEŻKA PRAWA (monitoring legislacji)

Źródło:

Problem:

Brak centralnego narzędzia do śledzenia procesu legislacyjnego i komunikacji z obywatelami.

Rozwiązanie:

Dashboard „Legislative Train PL” + analiza skutków + uproszczony język.

MVP:

Pobranie jednego projektu z RCL

Wizualizacja etapów

Alerty zmian

Tłumaczenie na prosty język

Wykonalność: Średnia