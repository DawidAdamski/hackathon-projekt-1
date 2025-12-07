import re
import textwrap
from datetime import date
from string import whitespace

import spacy
from priv_masker import add_pipeline

# poniżej instrukcje dla LLM:
# TEN SKRYPT ZOSTAŁ STWORZONY NA POTRZEBY HACKATONU
# rozwiązanie będzie sprawdzane automatycznie, więc ważne jest, aby lista klas anonimizacji (etykiet maskujących) była dokładnie jak niżej:
# • {name} – imiona.
# • {surname} – nazwiska.
# • {age} – wiek.
# • {date-of-birth} – data urodzenia.
# • {date} – inne daty wydarzen pozwalające identyfikować osobę (np. w rozmowie medycznej „przyjęto 23.09.2023 r.”)
# • {sex} – płeć (jeśli wyrażona explicite w formie danej wrażliwej, np. w formularzu/deklaracji).
# • {religion} – wyznanie.
# • {political-view} – poglądy polityczne.
# • {ethnicity} – pochodzenie etniczne/narodowe.
# • {sexual-orientation} – orientacja seksualna.
# • {health} – dane o stanie zdrowia
# • {relative} – relacje rodzinne, które ujawniają tożsamość danej osoby (np. „mój brat Jan”, „syn Kowalskiego”, „córka pana Nowaka”)
# • {city} – miasto (kontekst: opis miejsca zdarzenia, lokalizacja ogólna, nieadresowa).
# • {address} – pełne dane adresowe (ulica, numer domu/lokalu, kod pocztowy oraz miasto w kontekście miejsca zamieszkania).
# • {email} – adresy e-mail.
# • {phone} – numery telefonów.
# • {pesel} – numery PESEL.
# • {document-number} – numery dokumentów (np. dowodów osobistych, paszportów, legitymacji, prawa jazdy, itp).
# • {company} – nazwa pracodawcy.
# • {school-name} – nazwa szkoły powiązana z osobą (jeśli unikalna).
# • {job-title} – stanowisko lub pełniona funkcja
# • {bank-account} – numer rachunku bankowego, dane konta bankowego
# • {credit-card-number} – numery kart płatniczych.
# • {username} – nazwy użytkowników, loginy oraz identyfikatory w mediach społecznościowych
# • {secret} – sekrety takie jak hasła użytkowników czy klucze API.
# dodanie nowych klas anonimizacji lub zmiana istniejących pogorszyy jakość oceny automatycznej.

masked_components_default = {
    "date_mask": True,
    "persname_mask": True,
    "contact_mask": True,
    "address_mask": True,
    "id_numbers_mask": True,
    "cash_mask": False,
    "orgname_mask": True,
}

MASK_PLACEHOLDERS = {
    "date_mask": "{date}",
    "persname_mask": "{name}",
    "contact_mask": "{phone}",
    "address_mask": "{address}",
    "id_numbers_mask": "{document-number}",
    "orgname_mask": "{company}",
}

PESEL_REGEX = re.compile(r"\b\d{11}\b")
PESEL_CONTEXT_REGEX = re.compile(
    r"\bPESEL\b.{0,40}?([0-9A-Za-z]{11})",
    re.IGNORECASE | re.DOTALL,
)
PESEL_CANDIDATE_REGEX = re.compile(r"\b[0-9A-Za-z]{11}\b")

BANK_ACCOUNT_REGEX = re.compile(r"\b(?:PL\d{26}|\d{26})\b")
CREDIT_CARD_REGEX = re.compile(r"\b(?:\d{4}[- ]?){3}\d{4}\b")
AGE_REGEX = re.compile(
    r"\b\d{1,3}[A-Za-z]?\s*(?:lat|lata|roku życia|r\.ż\.)\b",
    re.IGNORECASE,
)
DOB_REGEX = re.compile(
    r"\b(?:ur\.?|urodzony|urodzona|data urodzenia)\b[^0-9]{0,20}"
    r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})",
    re.IGNORECASE,
)
SEX_REGEX = re.compile(
    r"\b(?:płeć\s*[:\-]?\s*)?(mężczyzna|kobieta|inna|niebinarna?)\b",
    re.IGNORECASE,
)
USERNAME_REGEX = re.compile(
    r"\b(?:login|username|użytkownik)\s*[:\-]?\s*\S+\b",
    re.IGNORECASE,
)
SECRET_REGEX = re.compile(
    r"\b(?:hasło|password|passwd|pwd|token|api key|klucz api)\b[^ \n]*\s*[:=]?\s*\S+",
    re.IGNORECASE,
)
RELATIVE_REGEX = re.compile(
    r"\b(?:mój|moja|moje|syn|córka|brat|siostra|ojciec|matka|mąż|żona)\s+"
    r"[A-ZŻŹĆŃŁÓŚĄĘ][a-zżźćńłóśąę]+\b"
)
RELATIVE_BY_SURNAME_REGEX = re.compile(
    r"\b(?:syn|córka)\s+pana\s+[A-ZŻŹĆŃŁÓŚĄĘ][a-zżźćńłóśąę]+\b",
    re.IGNORECASE,
)
CITY_REGEX = re.compile(
    r"\b(?:miasto|w mieście)\s+[A-ZŻŹĆŃŁÓŚĄĘ][a-zżźćńłóśąę]+\b",
    re.IGNORECASE,
)
RELIGION_REGEX = re.compile(
    r"\b(?:wyznanie|religia)\s*[:\-]?\s*\S+\b",
    re.IGNORECASE,
)
POLITICAL_REGEX = re.compile(
    r"\b(?:poglądy polityczne|preferencje polityczne|sympatie polityczne)\s*[:\-]?\s*[^.!\n]+",
    re.IGNORECASE,
)
ETHNICITY_REGEX = re.compile(
    r"\b(?:narodowość|pochodzenie)\s*[:\-]?\s*\S+\b",
    re.IGNORECASE,
)
SEXUAL_ORIENTATION_REGEX = re.compile(
    r"\b(?:orientacja seksualna)\s*[:\-]?\s*\S+\b",
    re.IGNORECASE,
)
HEALTH_REGEX = re.compile(
    r"\b(?:rozpoznanie|diagnoza|choruje na|leczony z powodu)\b[^.!\n]+",
    re.IGNORECASE,
)
COMPANY_REGEX = re.compile(
    r"\b(?:firma|przedsiębiorstwo|spółka)\s+[A-ZŻŹĆŃŁÓŚĄĘ][\w&\- ]+",
    re.IGNORECASE,
)
SCHOOL_REGEX = re.compile(
    r"\b(?:szkoła|liceum|technikum|uniwersytet|politechnika|akademia)\s+"
    r"[A-ZŻŹĆŃŁÓŚĄĘ][\w \-]+",
    re.IGNORECASE,
)
JOB_TITLE_REGEX = re.compile(
    r"\b(?:stanowisko|funkcja)\s*[:\-]?\s*[^,.\n]+",
    re.IGNORECASE,
)
USERNAME_SOCIAL_REGEX = re.compile(r"\B@[A-Za-z0-9_]{3,}\b")
EMAIL_REGEX = re.compile(
    r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b",
    re.IGNORECASE,
)
PHONE_REGEX = re.compile(
    r"\b(?:\+?\d{1,3}[- ]?)?(?:\d{3}[- ]?){2,3}\d{2,4}\b"
)

PHONE_CONTEXT_REGEX = re.compile(
    r"(?:(?:tel\.?|telefon|kom\.?|phone|fax|zadzwoń|zadzwon|kontakt)\s*(?:[:\-]|pod\s*numer)?\s*|\+)\s*([0-9OoqQbBgGhHiIlL ()+\-]{7,32})",
    re.IGNORECASE,
)

PHONE_LETTER_TO_DIGIT = {
    "O": "0",
    "o": "0",
    "Q": "0",
    "q": "0",
    "I": "1",
    "i": "1",
    "L": "1",
    "l": "1",
    "B": "8",
    "b": "8",
    "G": "9",
    "g": "9",
}

DOCUMENT_NUMBER_CONTEXT_REGEX = re.compile(
    r"\b(?:NIP|REGON|Nr|nr|ZDP|GK|GN|MAP|Ewid|EWID)\b",
    re.IGNORECASE,
)

MONTH_WORDS = {
    "stycznia",
    "lutego",
    "marca",
    "kwietnia",
    "maja",
    "czerwca",
    "lipca",
    "sierpnia",
    "września",
    "wrzesnia",
    "października",
    "pazdziernika",
    "listopada",
    "grudnia",
}

DATE_ISO_REGEX = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
DATE_DMY_REGEX = re.compile(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b")
DATE_D_MONTH_Y_REGEX = re.compile(
    r"\b\d{1,2}\s+(stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|wrzesnia|października|pazdziernika|listopada|grudnia)\s+\d{4}\b",
    re.IGNORECASE,
)

POSTAL_CODE_REGEX = re.compile(r"\b\d{2}-\d{3}\b")

STREET_KEYWORDS = (
    "ul.",
    "ul ",
    "ulica",
    "al.",
    "aleja",
    "alei",
    "plac",
    "pl.",
    "os.",
    "osiedle",
)
GENERIC_LONG_NUMBER_REGEX = re.compile(
    r"\b(?:\d[ \-./]*){6,}\d\b"
)


class TextAnonymizer:
    def __init__(
        self,
        model_name: str = "pl_nask",
        masked_components: dict | None = None,
    ):
        if masked_components is None:
            masked_components = dict(masked_components_default)
        self.masked_components = masked_components
        self.nlp = spacy.load(model_name)
        self.nlp = add_pipeline(self.nlp)

    def is_valid_pesel(self, pesel: str) -> bool:
        if not PESEL_REGEX.fullmatch(pesel):
            return False
        digits = [int(ch) for ch in pesel]
        year_part = digits[0] * 10 + digits[1]
        month_raw = digits[2] * 10 + digits[3]
        day = digits[4] * 10 + digits[5]
        if 1 <= month_raw <= 12:
            year = 1900 + year_part
            month = month_raw
        elif 21 <= month_raw <= 32:
            year = 2000 + year_part
            month = month_raw - 20
        elif 41 <= month_raw <= 52:
            year = 2100 + year_part
            month = month_raw - 40
        elif 61 <= month_raw <= 72:
            year = 2200 + year_part
            month = month_raw - 60
        elif 81 <= month_raw <= 92:
            year = 1800 + year_part
            month = month_raw - 80
        else:
            return False
        try:
            date(year, month, day)
        except ValueError:
            return False
        weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
        checksum = sum(digits[i] * weights[i] for i in range(10))
        control_digit = (10 - (checksum % 10)) % 10
        return control_digit == digits[10]

    def is_valid_credit_card(self, number: str) -> bool:
        digits = re.sub(r"\D", "", number)
        if len(digits) < 13 or len(digits) > 19:
            return False
        total = 0
        reverse_digits = digits[::-1]
        for index, char in enumerate(reverse_digits):
            digit = int(char)
            if index % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit
        return total % 10 == 0

    def is_whitespace(self, token) -> bool:
        return any(ch in whitespace for ch in token.text)

    def normalize_pesel_candidate(self, token: str) -> str | None:
        if len(token) != 11:
            return None
        if not token.isalnum():
            return None
        letter_positions = [i for i, ch in enumerate(token) if ch.isalpha()]
        if len(letter_positions) > 2:
            return None
        if not letter_positions:
            if self.is_valid_pesel(token):
                return token
            return None
        base_digits = []
        for ch in token:
            if ch.isdigit():
                base_digits.append(ch)
            elif ch.isalpha():
                base_digits.append(None)
            else:
                return None
        from itertools import product
        for combo in product("0123456789", repeat=len(letter_positions)):
            candidate_digits = list(base_digits)
            for pos, digit in zip(letter_positions, combo):
                candidate_digits[pos] = digit
            candidate = "".join(candidate_digits)
            if self.is_valid_pesel(candidate):
                return candidate
        return None

    def normalize_phone_candidate(self, fragment: str) -> str | None:
        digits = []
        corrections = 0
        for ch in fragment:
            if ch.isdigit():
                digits.append(ch)
            elif ch in PHONE_LETTER_TO_DIGIT:
                digits.append(PHONE_LETTER_TO_DIGIT[ch])
                corrections += 1
            elif ch in " -()+":
                continue
            elif ch.lower() in {"h"}:
                corrections += 1
            elif ch.isalpha():
                corrections += 1
            else:
                return None
        if len(digits) < 7:
            return None
        if corrections > 3:
            return None
        number = "".join(digits)
        if len(number) > 11:
            return None
        if len(set(number)) == 1:
            return None
        return number

    def is_date_like_fragment(self, fragment: str) -> bool:
        if DATE_ISO_REGEX.search(fragment):
            return True
        if DATE_DMY_REGEX.search(fragment):
            return True
        if DATE_D_MONTH_Y_REGEX.search(fragment):
            return True
        return False

    def should_mask_date_token(self, token) -> bool:
        text_val = token.text
        lower = text_val.lower()
        if re.search(r"\d{1,2}[./-]\d{1,2}[./-]\d{2,4}", text_val):
            return True
        if lower in MONTH_WORDS:
            return True
        doc = token.doc
        start = max(0, token.i - 3)
        end = min(len(doc), token.i + 4)
        window = " ".join(t.text.lower() for t in doc[start:end])
        date_keywords = [
            "z dnia",
            "data urodzenia",
            "urodzony",
            "urodzona",
            "urodz.",
            "rok",
            "r.",
            "r ",
            "dnia",
        ]
        if any(kw in window for kw in date_keywords):
            return True
        if any(month in window for month in MONTH_WORDS):
            return True
        return False

    def classify_address_text(self, fragment: str) -> str:
        if POSTAL_CODE_REGEX.search(fragment):
            return "{address}"
        lower = fragment.lower()
        for kw in STREET_KEYWORDS:
            if kw in lower:
                return "{address}"
        return "{city}"

    def placeholder_for_span(self, mask_name: str, fragment: str, tokens) -> str | None:
        if not fragment.strip():
            return None
        if mask_name == "persname_mask":
            has_last_name = any(getattr(t._, "priv_last_name", False) for t in tokens)
            if has_last_name and len(tokens) == 1:
                return "{surname}"
            return "{name}"
        if mask_name == "contact_mask":
            if "@" in fragment or "©" in fragment or "Q" in fragment:
                return "{email}"
            normalized = self.normalize_phone_candidate(fragment)
            if normalized is not None:
                return "{phone}"
            return "{phone}"
        if mask_name == "address_mask":
            normalized = self.normalize_phone_candidate(fragment)
            if normalized is not None:
                return "{phone}"
            return self.classify_address_text(fragment)
        if mask_name == "date_mask":
            if self.is_date_like_fragment(fragment) or any(
                self.should_mask_date_token(t) for t in tokens
            ):
                return "{date}"
            return None
        if mask_name == "id_numbers_mask":
            digits_only = re.sub(r"\D", "", fragment)
            if len(digits_only) == 11 and self.is_valid_pesel(digits_only):
                return "{pesel}"
            return "{document-number}"
        if mask_name == "orgname_mask":
            lower = fragment.lower()
            if any(
                keyword in lower
                for keyword in ["szkoła", "liceum", "uniwersytet", "politechnika", "akademia"]
            ):
                return "{school-name}"
            return "{company}"
        return MASK_PLACEHOLDERS.get(mask_name, "{secret}")

    def build_regex_spans(self, text: str):
        spans = []

        def add_span(start: int, end: int, placeholder: str):
            for existing_start, existing_end, _ in spans:
                if not (end <= existing_start or start >= existing_end):
                    return
            spans.append((start, end, placeholder))

        for match in PESEL_REGEX.finditer(text):
            if self.is_valid_pesel(match.group(0)):
                add_span(match.start(), match.end(), "{pesel}")

        for match in PESEL_CONTEXT_REGEX.finditer(text):
            add_span(match.start(1), match.end(1), "{pesel}")

        for match in PESEL_CANDIDATE_REGEX.finditer(text):
            raw = match.group(0)
            normalized = self.normalize_pesel_candidate(raw)
            if normalized is not None:
                add_span(match.start(), match.end(), "{pesel}")

        for match in DOB_REGEX.finditer(text):
            add_span(match.start(1), match.end(1), "{date-of-birth}")

        for match in DATE_ISO_REGEX.finditer(text):
            add_span(match.start(), match.end(), "{date}")

        for match in DATE_DMY_REGEX.finditer(text):
            add_span(match.start(), match.end(), "{date}")

        for match in DATE_D_MONTH_Y_REGEX.finditer(text):
            add_span(match.start(), match.end(), "{date}")

        for match in BANK_ACCOUNT_REGEX.finditer(text):
            add_span(match.start(), match.end(), "{bank-account}")

        for match in CREDIT_CARD_REGEX.finditer(text):
            if self.is_valid_credit_card(match.group(0)):
                add_span(match.start(), match.end(), "{credit-card-number}")

        for match in PHONE_CONTEXT_REGEX.finditer(text):
            raw_fragment = match.group(1)
            normalized = self.normalize_phone_candidate(raw_fragment)
            if normalized is not None:
                start = match.start(1)
                end = match.end(1)
                add_span(start, end, "{phone}")

        for m in re.finditer(r"\b(?:NIP|REGON|Nr|nr|ZDP|GK|GN|MAP|Ewid|EWID)\b[^\n\r]{0,30}", text):
            prefix_end = m.end()
            num_match = re.search(r"\d[\d\s\-]{5,}", text[prefix_end:prefix_end + 40])
            if num_match:
                start = prefix_end + num_match.start()
                end = prefix_end + num_match.end()
                fragment = text[start:end]
                if self.is_date_like_fragment(fragment):
                    add_span(start, end, "{date}")
                else:
                    add_span(start, end, "{document-number}")

        pattern_placeholders = [
            (AGE_REGEX, "{age}"),
            (SEX_REGEX, "{sex}"),
            (USERNAME_REGEX, "{username}"),
            (SECRET_REGEX, "{secret}"),
            (RELATIVE_REGEX, "{relative}"),
            (RELATIVE_BY_SURNAME_REGEX, "{relative}"),
            (CITY_REGEX, "{city}"),
            (RELIGION_REGEX, "{religion}"),
            (POLITICAL_REGEX, "{political-view}"),
            (ETHNICITY_REGEX, "{ethnicity}"),
            (SEXUAL_ORIENTATION_REGEX, "{sexual-orientation}"),
            (HEALTH_REGEX, "{health}"),
            (COMPANY_REGEX, "{company}"),
            (SCHOOL_REGEX, "{school-name}"),
            (JOB_TITLE_REGEX, "{job-title}"),
            (USERNAME_SOCIAL_REGEX, "{username}"),
            (EMAIL_REGEX, "{email}"),
        ]

        for pattern, placeholder in pattern_placeholders:
            for match in pattern.finditer(text):
                add_span(match.start(), match.end(), placeholder)

        for match in PHONE_REGEX.finditer(text):
            start, end = match.start(), match.end()
            overlap = False
            for es, ee, _ in spans:
                if not (end <= es or start >= ee):
                    overlap = True
                    break
            if overlap:
                continue
            prefix = text[max(0, start - 40):start].lower()
            if DOCUMENT_NUMBER_CONTEXT_REGEX.search(prefix):
                add_span(start, end, "{document-number}")
            else:
                add_span(start, end, "{phone}")

        for match in GENERIC_LONG_NUMBER_REGEX.finditer(text):
            start, end = match.start(), match.end()
            fragment = text[start:end]
            overlap = False
            for es, ee, _ in spans:
                if not (end <= es or start >= ee):
                    overlap = True
                    break
            if overlap:
                continue
            normalized_phone = self.normalize_phone_candidate(fragment)
            if normalized_phone is not None:
                add_span(start, end, "{phone}")
                continue
            add_span(start, end, "{document-number}")

        spans.sort(key=lambda span: span[0])
        return spans

    def build_token_spans(self, doc, text: str, enabled_masks, regex_spans):
        spans = []
        regex_ranges = [(s, e) for s, e, _ in regex_spans]

        def is_covered(start: int, end: int) -> bool:
            for rs, re_ in regex_ranges:
                if not (end <= rs or start >= re_):
                    return True
            return False

        i = 0
        n = len(doc)
        while i < n:
            token = doc[i]
            if token.is_space or token.is_punct:
                i += 1
                continue
            start_char = token.idx
            end_char = token.idx + len(token.text)
            if is_covered(start_char, end_char):
                i += 1
                continue
            mask_name = getattr(token._, "mask", None)
            if mask_name not in enabled_masks:
                i += 1
                continue
            start_token = i
            end_token = i + 1
            while end_token < n:
                t = doc[end_token]
                if t.is_space or t.is_punct:
                    break
                t_start = t.idx
                t_end = t.idx + len(t.text)
                if is_covered(t_start, t_end):
                    break
                if getattr(t._, "mask", None) != mask_name:
                    break
                end_token += 1
            span_start = doc[start_token].idx
            span_end = doc[end_token - 1].idx + len(doc[end_token - 1].text)
            fragment = text[span_start:span_end]
            placeholder = self.placeholder_for_span(mask_name, fragment, doc[start_token:end_token])
            if placeholder:
                spans.append((span_start, span_end, placeholder))
            i = end_token

        spans.sort(key=lambda s: s[0])
        return spans

    def merge_adjacent_same_placeholders(self, text: str, spans):
        if not spans:
            return spans
        merged = [list(spans[0])]
        for start, end, placeholder in spans[1:]:
            last_start, last_end, last_placeholder = merged[-1]
            if placeholder == last_placeholder:
                between = text[last_end:start]
                if between.strip(" -") == "":
                    merged[-1][1] = end
                    continue
            merged.append([start, end, placeholder])
        return [tuple(m) for m in merged]

    def apply_spans(self, text: str, spans):
        if not spans:
            return text
        parts = []
        last_index = 0
        for start, end, placeholder in spans:
            if start > last_index:
                parts.append(text[last_index:start])
            fragment = text[start:end]
            m = re.search(r"\s+$", fragment)
            trailing_ws = m.group(0) if m else ""
            parts.append(placeholder + trailing_ws)
            last_index = end
        if last_index < len(text):
            parts.append(text[last_index:])
        return "".join(parts)

    def mask(self, text: str) -> str:
        doc = self.nlp(text)
        enabled_masks = [
            component for component, enabled in self.masked_components.items() if enabled
        ]
        regex_spans = self.build_regex_spans(text)
        token_spans = self.build_token_spans(doc, text, enabled_masks, regex_spans)
        all_spans = sorted(regex_spans + token_spans, key=lambda s: s[0])
        all_spans = self.merge_adjacent_same_placeholders(text, all_spans)
        result = self.apply_spans(text, all_spans)
        return result

    def print_comparison(self, original: str, masked: str, index: int) -> None:
        separator = "=" * 120
        print(f"\n{separator}")
        print(f"PRZYKŁAD {index + 1}")
        print(separator)
        print("\n[ORYGINALNY TEKST]")
        wrapped_original = textwrap.fill(original, width=120)
        print(wrapped_original)
        print("\n[TEKST ZAMASKOWANY]")
        wrapped_masked = textwrap.fill(masked, width=120)
        print(wrapped_masked)
        print(f"\n{separator}\n")


if __name__ == "__main__":
    import random

    anonymizer = TextAnonymizer()
    test_data_path = "nask_train/anonymized.txt"
    with open(test_data_path, "r", encoding="utf-8") as f:
        all_lines = [line.strip() for line in f.readlines()]

    sample_size = min(100, len(all_lines))
    test_lines = random.sample(all_lines, sample_size)

    for idx, text in enumerate(test_lines):
        masked_text = anonymizer.mask(text)
        anonymizer.print_comparison(text, masked_text, idx)
