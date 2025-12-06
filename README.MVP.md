# Minimum Viable Product (MVP) Analysis
## Dane bez twarzy

> **Zobacz także:** [Product Requirements Document (PRD)](README.PRD.md)

---

## 1. Definicja Produktu

### Zwięzły opis produktu (The "Elevator Pitch")
Budujemy bibliotekę Python, która automatycznie wykrywa i anonimizuje dane osobowe w tekstach konwersacyjnych w języku polskim, zastępując je tokenami zastępczymi (np. `{name}`, `{pesel}`). Rozwiązanie jest przeznaczone do integracji z potokami przetwarzania danych dla treningu modelu PLLuM.

### Kluczowy problem (Core Pain Point)
Potrzeba precyzyjnej anonimizacji danych osobowych w tekstach polskich z zachowaniem struktury gramatycznej i sensu, przy jednoczesnym rozróżnianiu kontekstu (np. miasto jako miejsce zdarzenia vs adres zamieszkania) oraz obsłudze fleksji języka polskiego.

---

## 2. Zakres MVP

### Najkrótsza ścieżka do wartości (Kluczowe funkcjonalności MVP)

**Core MVP (Minimum dla oceny):**
- Biblioteka Python przyjmująca tekst i zwracająca zanonimizowaną wersję
- Wykrywanie i anonimizacja **podstawowych kategorii PII:**
  - `{name}` – imiona
  - `{surname}` – nazwiska
  - `{pesel}` – numery PESEL
  - `{email}` – adresy e-mail
  - `{phone}` – numery telefonów
  - `{address}` – podstawowe adresy (z rozróżnieniem kontekstu)
- Podstawowe rozróżnianie kontekstu: `{city}` vs `{address}`
- Obsługa fleksji polskiej dla imion i nazwisk

**Rozszerzone MVP (dla wyższej oceny):**
- Dodatkowe kategorie: `{age}`, `{date-of-birth}`, `{document-number}`, `{bank-account}`
- Moduł generacji danych syntetycznych z zachowaniem morfologii
- Większa precyzja w rozróżnianiu kontekstu

### Ścieżki użytkownika (User Stories dla MVP)

- **Jako Inżynier Danych**, chcę zintegrować bibliotekę z pipeline'em przetwarzania danych, aby automatycznie anonimizować teksty przed treningiem modelu PLLuM.

- **Jako Badacz ML**, chcę przetworzyć zbiór tekstów konwersacyjnych i otrzymać zanonimizowaną wersję z poprawnie rozpoznanymi kategoriami PII, zachowując strukturę gramatyczną.

### Poza zakresem MVP (Out of Scope)

- Interfejs webowy (rozwiązanie to biblioteka Python, nie aplikacja webowa)
- Wszystkie 24+ kategorie PII (MVP skupia się na podstawowych)
- Zaawansowany moduł generacji syntetycznej (może być uproszczony w MVP)
- Obsługa plików binarnych (.docx) – tylko tekst surowy
- Zewnętrzne API (rozwiązanie musi być offline)

---

## 3. Kryteria Sukcesu MVP

### Metryki sukcesu

**Kryteria oceny (zgodnie z zadaniem):**
- **F1-score** dla wszystkich klas ≥ 0.85 (35% wagi oceny)
- **Minimalizacja False Negatives** – wykrycie wszystkich danych wrażliwych jest krytyczne
- **Wydajność:** Przetwarzanie próbki danych w rozsądnym czasie (20% wagi)
- **Poprawność rozróżniania kontekstu:** Szczególnie `{city}` vs `{address}` oraz fleksja (15% wagi)
- **Jakość kodu i dokumentacja:** Łatwość wdrożenia, konteneryzacja (20% wagi)

**Metryki techniczne:**
- Biblioteka zwraca wynik dla tekstu o długości 5000 znaków w czasie poniżej 10 sekund
- Rozwiązanie działa offline (bez zewnętrznych API)
- Kod jest gotowy do integracji z data pipelines

---

## 4. Sugerowany stack technologiczny (Python)

### Biblioteka Python
Rozwiązanie powinno być **biblioteką Python** (nie aplikacją webową), gotową do integracji z data pipelines.

### Analiza danych/AI

**Dozwolone technologie (offline, open-source):**
- **spaCy** z modelem dla języka polskiego (`pl_core_news_lg`) do podstawowego NER
- **HuggingFace Transformers** z modelami polskimi (HerBERT, PolBERT, PLLuM)
- **Flair** – biblioteka NLP z modelami dla języka polskiego
- **Wyrażenia regularne** (moduł `re`) do niezawodnego wykrywania wzorców o stałej strukturze (PESEL, e-mail, telefon, numery dokumentów)

**Podejście hybrydowe (rekomendowane):**
- Kombinacja RegEx (dla struktur stałych) + modele ML (dla kontekstu i fleksji)
- To podejście jest punktowane w kryteriach oceny (10% za pomysłowość)

### Generacja danych syntetycznych
- Biblioteki do morfologii polskiej (np. `pymorphy2`, `morfeusz2`)
- Generatory wartości z kategorii z zachowaniem odmiany

### Inne
- **Docker** – konteneryzacja rozwiązania (wymagane dla łatwości wdrożenia)
- **pytest** – testy jednostkowe
- **README** z instrukcją instalacji (`pip install -r requirements.txt`)

---

## 5. Ocena Wykonalności (Feasibility)

### Możliwość wykonania w 48h
**Wysoka**

### Uzasadnienie
Zakres MVP skupia się na podstawowych kategoriach PII (name, surname, pesel, email, phone, address) oraz kluczowym rozróżnianiu kontekstu. Podejście hybrydowe (RegEx + ML) pozwala na szybką implementację przy zachowaniu akceptowalnej dokładności. Największe wyzwania:

1. **Rozróżnianie kontekstu** – wymaga analizy semantycznej, ale można użyć prostych heurystyk w MVP
2. **Fleksja polska** – modele NER + słowniki odmian mogą pomóc
3. **Offline processing** – wyklucza zewnętrzne API, ale dostępne są dobre modele open-source

**Ryzyka:**
- Niska dokładność dla rzadkich kategorii PII (można skupić się na podstawowych w MVP)
- Wydajność przy dużych zbiorach danych (optymalizacja może być w wersji rozszerzonej)
- Generacja syntetyczna z morfologią (może być uproszczona w MVP)

**Strategia:** Zaimplementować solidne podstawy (6-8 kategorii) z dobrym F1-score, a następnie rozszerzać o dodatkowe kategorie i moduł syntetyczny.

