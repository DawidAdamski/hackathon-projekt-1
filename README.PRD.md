# Product Requirements Document (PRD)
## Dane bez twarzy

**Organizator:** Konsorcjum PLLuM (Polish Large Language Model) / NASK

---

## 1. Problem do rozwiązania (The "Why")

### Opis problemu
Aby wytrenować model PLLuM (Polish Large Language Model), potrzebne są ogromne zbiory danych tekstowych. Znaczną część tych zasobów stanowią zapisy konwersacji, fragmenty e-maili, posty z forów dyskusyjnych czy zgłoszenia urzędowe. Problemem jest występowanie w tych tekstach Danych Osobowych. Zgodnie z RODO oraz standardami etycznymi, nie możemy trenować modelu na surowych danych zawierających imiona, nazwiska, numery PESEL czy adresy, ponieważ istnieje ryzyko, że model "zapamięta" te dane i ujawni je w przyszłości.

Obecnie stosowane rozwiązania oparte na zasobach słownikowych są niewystarczające, szczególnie w przypadku języka polskiego (fleksja, skomplikowana gramatyka) oraz konieczności rozróżnienia kontekstu (np. miasto będące miejscem akcji vs miasto zamieszkania). Potrzebujemy rozwiązania, które z chirurgiczną precyzją wyczyści dane, pozostawiając jednocześnie ich strukturę gramatyczną i sens, co jest kluczowe dla jakości treningu modelu.

### Grupa docelowa
Użytkownikami końcowymi tego rozwiązania będą **Inżynierowie Danych i Badacze ML** z zespołu PLLuM. Rozwiązanie powinno być łatwe do integracji z potokami przetwarzania danych (data pipelines).

---

## 2. Proponowane rozwiązanie (The "What")

### Główny cel
Stworzenie algorytmu lub modelu uczenia maszynowego, który automatycznie wykryje w tekstach konwersacyjnych w języku polskim określone kategorie danych wrażliwych i zastąpi je odpowiednimi etykietami (tokenami zastępczymi, np. `{name}`, `{pesel}`).

Kluczową trudnością jest kontekstowość wypowiedzi. System musi radzić sobie z tekstami nieformalnymi, pojedynczymi zapytaniami oraz dłuższymi fragmentami dialogów. Rozwiązanie musi poprawnie klasyfikować dane, odróżniając np. miasto wspomniane w kontekście opisu wycieczki `{city}` od miasta będącego częścią adresu zamieszkania `{address}`.

### Kluczowe funkcjonalności

**Wymagane klasy anonimizacji** (24+ kategorie):

**Dane identyfikacyjne osobowe:**
- `{name}` – imiona
- `{surname}` – nazwiska
- `{age}` – wiek
- `{date-of-birth}` – data urodzenia
- `{date}` – inne daty wydarzeń pozwalające identyfikować osobę
- `{sex}` – płeć
- `{religion}` – wyznanie
- `{political-view}` – poglądy polityczne
- `{ethnicity}` – pochodzenie etniczne/narodowe
- `{sexual-orientation}` – orientacja seksualna
- `{health}` – dane o stanie zdrowia
- `{relative}` – relacje rodzinne ujawniające tożsamość

**Dane kontaktowe i lokalizacyjne:**
- `{city}` – miasto (kontekst: opis miejsca zdarzenia, nieadresowa)
- `{address}` – pełne dane adresowe (ulica, numer, kod pocztowy, miasto w kontekście zamieszkania)
- `{email}` – adresy e-mail
- `{phone}` – numery telefonów

**Identyfikatory dokumentów:**
- `{pesel}` – numery PESEL
- `{document-number}` – numery dokumentów (dowód, paszport, prawo jazdy)

**Dane zawodowe i edukacyjne:**
- `{company}` – nazwa pracodawcy
- `{school-name}` – nazwa szkoły
- `{job-title}` – stanowisko/funkcja

**Informacje finansowe:**
- `{bank-account}` – numer rachunku bankowego
- `{credit-card-number}` – numery kart płatniczych

**Identyfikatory cyfrowe:**
- `{username}` – loginy, identyfikatory w mediach społecznościowych
- `{secret}` – hasła, klucze API

**Moduł generacji danych syntetycznych:**
- Podmiana etykiet na pasujące wartości z kategorii
- Zachowanie dopasowania morfologicznego do reszty tekstu (np. "Warszawskiej" → `{city}` → "Krakowskiej")

---

## 3. Oczekiwany rezultat (Deliverable)

### Forma projektu
Komponent programistyczny (biblioteka Python / skrypt), który przyjmuje na wejściu surowy tekst i zwraca jego zanonimizowaną wersję z podmienionymi encjami.

**Przykład:**
- **Wejście:** "Nazywam się Jan Kowalski, mój PESEL to 90010112345. Mieszkam w Warszawie przy ulicy Długiej 5."
- **Wyjście:** "Nazywam się {name} {surname}, mój PESEL to {pesel}. Mieszkam w {address}."

Ważne jest, aby narzędzie nie usuwało całych zdań, lecz podmieniało konkretne frazy na tokeny zastępcze.

### Wymagania formalne
- Repozytorium kodu (GitHub/GitLab) z pełnym kodem źródłowym
- Plik README z instrukcją instalacji i uruchomienia
- Prezentacja PDF (maksymalnie 5 slajdów) opisująca podejście

### Kryteria oceny

- **Skuteczność anonimizacji (F1-score)** — 35% (najważniejsze kryterium: bezpieczeństwo danych)
- **Wydajność, jakość kodu oraz łatwość wdrożenia** — 20%
- **Skuteczny moduł do generacji danych syntetycznych** — 20%
- **Poprawność rozróżniania kontekstu** — 15% (szczególnie {city} vs {address} oraz fleksja)
- **Pomysłowość podejścia** — 10% (np. hybrydowe łączenie RegEx z modelami ML)

**Dodatkowo:** Nacisk na minimalizację False Negatives (FN) – sytuacji, gdzie dane wrażliwe nie zostały wykryte (błąd krytyczny).

---

## 4. Potencjalne wyzwania i ryzyka

### Rozwiązanie offline (KRYTYCZNE)
Ze względów bezpieczeństwa narzędzie **NIE MOŻE korzystać z zewnętrznych API** (np. OpenAI, Google Cloud NLP). Całe przetwarzanie musi odbywać się lokalnie.

### Dokładność NER dla języka polskiego
Gotowe modele NER mogą mieć trudności z precyzyjnym rozpoznawaniem wszystkich typów PII, zwłaszcza w kontekście fleksji polskiej. Poleganie wyłącznie na nich może prowadzić do przeoczeń lub fałszywych alarmów.

### Rozróżnianie kontekstu
Kluczowe wyzwanie: odróżnienie `{city}` (miasto jako miejsce zdarzenia) od `{address}` (miasto w kontekście adresu zamieszkania). System musi poprawnie klasyfikować dane w zależności od kontekstu wypowiedzi.

### Fleksja i morfologia języka polskiego
Poprawna detekcja `{name}`/`{surname}` w różnych odmianach fleksyjnych oraz zapewnienie morfologicznej spójności przy generacji danych syntetycznych (np. "Warszawskiej" → "Krakowskiej").

### Wydajność i skalowalność
Rozwiązanie powinno być skalowalne – docelowo będzie przetwarzać **terabajty danych**, więc wydajność inferencji jest istotna. Przetwarzanie dużych dokumentów za pomocą zaawansowanych modeli AI może być wolne i wymagać znacznych zasobów obliczeniowych.

### Dozwolone technologie
Można korzystać z modeli językowych open-source (np. HerBERT, PolBERT, PLLuM) oraz bibliotek NLP (HuggingFace Transformers, Flair, SpaCy), pod warunkiem, że ich licencja pozwala na komercyjne użycie.

