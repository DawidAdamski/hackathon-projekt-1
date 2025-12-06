Nazwa Projektu: Dane bez twarzy

Organizator: Fundacja Tech for Society

1. Problem do rozwiązania (The "Why")
Opis problemu: W dobie RODO, ręczna anonimizacja dokumentów jest procesem czasochłonnym, kosztownym i podatnym na błędy. Organizacje (firmy, instytucje publiczne, ośrodki badawcze) potrzebują narzędzia do automatycznego usuwania danych osobowych (PII) z dokumentów tekstowych, aby móc je bezpiecznie przetwarzać i udostępniać do analizy.

Grupa docelowa: Głównymi beneficjentami są użytkownicy nietechniczni, tacy jak prawnicy, analitycy biznesowi, pracownicy administracji publicznej oraz badacze, którzy muszą pracować na zanonimizowanych danych.

2. Proponowane rozwiązanie (The "What")
Główny cel: Stworzenie szybkiego, dokładnego i łatwego w użyciu narzędzia, które automatycznie identyfikuje i anonimizuje dane osobowe w dokumentach tekstowych w języku polskim.

Kluczowe funkcjonalności (zgodnie z PDF):

Interfejs do wgrywania plików (.txt, .docx) lub wklejania tekstu.

Mechanizm identyfikacji PII (imiona, nazwiska, PESEL, numery telefonów, e-maile, adresy, NIP).

Możliwość zastąpienia wykrytych danych zdefiniowanymi placeholderami (np. [IMIĘ], [PESEL]).

Wyświetlenie zanonimizowanego tekstu i opcja jego pobrania.

3. Oczekiwany rezultat (Deliverable)
Forma projektu: Działający prototyp aplikacji, np. webowej.

Kryteria oceny:

Skuteczność i dokładność anonimizacji (kryterium kluczowe).

Innowacyjność podejścia (wykorzystanie modeli ML/AI).

Jakość działającego prototypu i UX (User Experience).

Wykonalność i potencjał do dalszego rozwoju.

4. Potencjalne wyzwania i ryzyka
Dokładność NER dla języka polskiego: Gotowe modele NER mogą mieć trudności z precyzyjnym rozpoznawaniem wszystkich typów PII, zwłaszcza niestandardowych adresów. Poleganie wyłącznie na nich może prowadzić do przeoczeń lub fałszywych alarmów.

Obsługa formatu .docx: Parsowanie plików .docx z zachowaniem oryginalnego formatowania po anonimizacji jest złożone. Prosta ekstrakcja tekstu jest łatwa, ale odtworzenie struktury dokumentu w ramach hackathonu jest dużym wyzwaniem.

Wydajność: Przetwarzanie dużych dokumentów za pomocą zaawansowanych modeli AI (np. z biblioteki transformers) może być wolne i wymagać znacznych zasobów obliczeniowych, co negatywnie wpłynie na doświadczenie użytkownika w aplikacji webowej.

Analiza MVP (Minimum Viable Product)
5. Definicja Produktu
Zwięzły opis produktu (The "Elevator Pitch"): Budujemy prostą aplikację webową, która pozwala użytkownikowi wkleić tekst w języku polskim i natychmiast otrzymać jego wersję z automatycznie usuniętymi kluczowymi danymi osobowymi (imiona, nazwiska, PESEL).

Kluczowy problem (Core Pain Point): Umożliwienie błyskawicznej i łatwej anonimizacji fragmentów tekstu bez potrzeby manualnej, żmudnej pracy i specjalistycznej wiedzy.

6. Zakres MVP
Najkrótsza ścieżka do wartości (Kluczowe funkcjonalności MVP):

Prosty interfejs webowy z jednym polem do wklejenia tekstu.

Backendowy mechanizm anonimizacji, który identyfikuje i zastępuje tylko imiona, nazwiska, numery PESEL i adresy e-mail.

Wyświetlenie zanonimizowanego tekstu w drugim polu tekstowym na tej samej stronie.

Ścieżki użytkownika (User Stories dla MVP):

Jako prawnik, chcę wkleić fragment umowy do aplikacji i natychmiast otrzymać tekst z zanonimizowanymi nazwiskami i numerami PESEL, aby móc go bezpiecznie przesłać dalej.

Jako pracownik HR, chcę wkleić treść CV i otrzymać wersję bez danych kontaktowych (e-mail), aby udostępnić ją wewnątrz firmy zgodnie z zasadami.

Poza zakresem MVP (Out of Scope):

Obsługa wgrywania/pobierania plików (np. .txt, .docx).

Identyfikacja złożonych PII, takich jak adresy zamieszkania czy numery NIP.

Możliwość konfiguracji placeholderów przez użytkownika.

System logowania czy historia przetwarzanych dokumentów.

7. Kryteria Sukcesu MVP
Metryki sukcesu:

Aplikacja zwraca wynik dla tekstu o długości 5000 znaków w czasie poniżej 10 sekund.

Skuteczność (F1-score) w wykrywaniu imion, nazwisk i numerów PESEL na przygotowanym zestawie testowym jest wyższa niż 85%.

Prototyp jest w stanie obsłużyć co najmniej 5 jednoczesnych zapytań bez awarii.

Realizacja Techniczna
8. Sugerowany stack technologiczny (Python)
Backend/API: FastAPI – ze względu na wysoką wydajność, prostotę użycia i automatycznie generowaną dokumentację, co jest kluczowe w warunkach hackathonu.

Analiza danych/AI:

spaCy z modelem dla języka polskiego (pl_core_news_lg) do podstawowego NER (identyfikacja osób).

Wyrażenia regularne (moduł re) do niezawodnego wykrywania wzorców o stałej strukturze, takich jak PESEL, NIP, adresy e-mail i numery telefonów.

Interfejs użytkownika (jeśli dotyczy): Streamlit – pozwala na błyskawiczne stworzenie interaktywnego interfejsu webowego bezpośrednio w Pythonie, bez konieczności pisania kodu HTML/CSS/JS. Jest idealny do szybkiego prototypowania.

Inne (np. bazy danych, scraping): Brak – dla zdefiniowanego MVP żadne dodatkowe narzędzia nie są potrzebne.

9. Ocena Wykonalności (Feasibility)
Możliwość wykonania w 48h: Wysoka

Uzasadnienie: Zakres MVP jest celowo wąski i skupia się na kluczowych funkcjonalnościach. Wykorzystanie bibliotek takich jak Streamlit (dla UI) oraz połączenie spaCy z wyrażeniami regularnymi (dla logiki) drastycznie skraca czas dewelopmentu. Największe ryzyko – niska dokładność modelu NER – jest łagodzone przez użycie regexów dla danych o przewidywalnej strukturze. Rezygnacja z obsługi plików na rzecz wklejanego tekstu eliminuje złożoność związaną z parsowaniem.