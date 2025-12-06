# Product Requirements Document (PRD)
## Dane bez twarzy

**Organizator:** Fundacja Tech for Society

---

## 1. Problem do rozwiązania (The "Why")

### Opis problemu
W dobie RODO, ręczna anonimizacja dokumentów jest procesem czasochłonnym, kosztownym i podatnym na błędy. Organizacje (firmy, instytucje publiczne, ośrodki badawcze) potrzebują narzędzia do automatycznego usuwania danych osobowych (PII) z dokumentów tekstowych, aby móc je bezpiecznie przetwarzać i udostępniać do analizy.

### Grupa docelowa
Głównymi beneficjentami są użytkownicy nietechniczni, tacy jak prawnicy, analitycy biznesowi, pracownicy administracji publicznej oraz badacze, którzy muszą pracować na zanonimizowanych danych.

---

## 2. Proponowane rozwiązanie (The "What")

### Główny cel
Stworzenie szybkiego, dokładnego i łatwego w użyciu narzędzia, które automatycznie identyfikuje i anonimizuje dane osobowe w dokumentach tekstowych w języku polskim.

### Kluczowe funkcjonalności (zgodnie z PDF)

- Interfejs do wgrywania plików (.txt, .docx) lub wklejania tekstu.
- Mechanizm identyfikacji PII (imiona, nazwiska, PESEL, numery telefonów, e-maile, adresy, NIP).
- Możliwość zastąpienia wykrytych danych zdefiniowanymi placeholderami (np. [IMIĘ], [PESEL]).
- Wyświetlenie zanonimizowanego tekstu i opcja jego pobrania.

---

## 3. Oczekiwany rezultat (Deliverable)

### Forma projektu
Działający prototyp aplikacji, np. webowej.

### Kryteria oceny

- Skuteczność i dokładność anonimizacji (kryterium kluczowe).
- Innowacyjność podejścia (wykorzystanie modeli ML/AI).
- Jakość działającego prototypu i UX (User Experience).
- Wykonalność i potencjał do dalszego rozwoju.

---

## 4. Potencjalne wyzwania i ryzyka

### Dokładność NER dla języka polskiego
Gotowe modele NER mogą mieć trudności z precyzyjnym rozpoznawaniem wszystkich typów PII, zwłaszcza niestandardowych adresów. Poleganie wyłącznie na nich może prowadzić do przeoczeń lub fałszywych alarmów.

### Obsługa formatu .docx
Parsowanie plików .docx z zachowaniem oryginalnego formatowania po anonimizacji jest złożone. Prosta ekstrakcja tekstu jest łatwa, ale odtworzenie struktury dokumentu w ramach hackathonu jest dużym wyzwaniem.

### Wydajność
Przetwarzanie dużych dokumentów za pomocą zaawansowanych modeli AI (np. z biblioteki transformers) może być wolne i wymagać znacznych zasobów obliczeniowych, co negatywnie wpłynie na doświadczenie użytkownika w aplikacji webowej.

