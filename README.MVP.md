# Minimum Viable Product (MVP) Analysis
## Dane bez twarzy

> **Zobacz także:** [Product Requirements Document (PRD)](README.PRD.md)

---

## 1. Definicja Produktu

### Zwięzły opis produktu (The "Elevator Pitch")
Budujemy prostą aplikację webową, która pozwala użytkownikowi wkleić tekst w języku polskim i natychmiast otrzymać jego wersję z automatycznie usuniętymi kluczowymi danymi osobowymi (imiona, nazwiska, PESEL).

### Kluczowy problem (Core Pain Point)
Umożliwienie błyskawicznej i łatwej anonimizacji fragmentów tekstu bez potrzeby manualnej, żmudnej pracy i specjalistycznej wiedzy.

---

## 2. Zakres MVP

### Najkrótsza ścieżka do wartości (Kluczowe funkcjonalności MVP)

- Prosty interfejs webowy z jednym polem do wklejenia tekstu.
- Backendowy mechanizm anonimizacji, który identyfikuje i zastępuje tylko imiona, nazwiska, numery PESEL i adresy e-mail.
- Wyświetlenie zanonimizowanego tekstu w drugim polu tekstowym na tej samej stronie.

### Ścieżki użytkownika (User Stories dla MVP)

- **Jako prawnik**, chcę wkleić fragment umowy do aplikacji i natychmiast otrzymać tekst z zanonimizowanymi nazwiskami i numerami PESEL, aby móc go bezpiecznie przesłać dalej.

- **Jako pracownik HR**, chcę wkleić treść CV i otrzymać wersję bez danych kontaktowych (e-mail), aby udostępnić ją wewnątrz firmy zgodnie z zasadami.

### Poza zakresem MVP (Out of Scope)

- Obsługa wgrywania/pobierania plików (np. .txt, .docx).
- Identyfikacja złożonych PII, takich jak adresy zamieszkania czy numery NIP.
- Możliwość konfiguracji placeholderów przez użytkownika.
- System logowania czy historia przetwarzanych dokumentów.

---

## 3. Kryteria Sukcesu MVP

### Metryki sukcesu

- Aplikacja zwraca wynik dla tekstu o długości 5000 znaków w czasie poniżej 10 sekund.
- Skuteczność (F1-score) w wykrywaniu imion, nazwisk i numerów PESEL na przygotowanym zestawie testowym jest wyższa niż 85%.
- Prototyp jest w stanie obsłużyć co najmniej 5 jednoczesnych zapytań bez awarii.

---

## 4. Sugerowany stack technologiczny (Python)

### Backend/API
**FastAPI** – ze względu na wysoką wydajność, prostotę użycia i automatycznie generowaną dokumentację, co jest kluczowe w warunkach hackathonu.

### Analiza danych/AI

- **spaCy** z modelem dla języka polskiego (`pl_core_news_lg`) do podstawowego NER (identyfikacja osób).
- **Wyrażenia regularne** (moduł `re`) do niezawodnego wykrywania wzorców o stałej strukturze, takich jak PESEL, NIP, adresy e-mail i numery telefonów.

### Interfejs użytkownika
**Streamlit** – pozwala na błyskawiczne stworzenie interaktywnego interfejsu webowego bezpośrednio w Pythonie, bez konieczności pisania kodu HTML/CSS/JS. Jest idealny do szybkiego prototypowania.

### Inne
Brak – dla zdefiniowanego MVP żadne dodatkowe narzędzia nie są potrzebne.

---

## 5. Ocena Wykonalności (Feasibility)

### Możliwość wykonania w 48h
**Wysoka**

### Uzasadnienie
Zakres MVP jest celowo wąski i skupia się na kluczowych funkcjonalnościach. Wykorzystanie bibliotek takich jak Streamlit (dla UI) oraz połączenie spaCy z wyrażeniami regularnymi (dla logiki) drastycznie skraca czas dewelopmentu. Największe ryzyko – niska dokładność modelu NER – jest łagodzone przez użycie regexów dla danych o przewidywalnej strukturze. Rezygnacja z obsługi plików na rzecz wklejanego tekstu eliminuje złożoność związaną z parsowaniem.

