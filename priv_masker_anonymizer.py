import re
import textwrap
from datetime import date
from string import whitespace

import spacy
from priv_masker import add_pipeline

masked_components = {
    "date_mask": True,
    "persname_mask": True,
    "contact_mask": True,
    "address_mask": True,
    "id_numbers_mask": True,
    "cash_mask": True,
    "orgname_mask": True,
}

MASK_PLACEHOLDERS = {
    "date_mask": "{date}",
    "persname_mask": "{name}",
    "contact_mask": "{phone}",
    "address_mask": "{address}",
    "id_numbers_mask": "{document-number}",
    "cash_mask": "{cash}",
    "orgname_mask": "{company}",
}

PESEL_REGEX = re.compile(r"\b\d{11}\b")
PESEL_CONTEXT_REGEX = re.compile(r"\bPESEL\b[^0-9A-Za-z]{0,10}([0-9A-Za-z]{11})", re.IGNORECASE)
BANK_ACCOUNT_REGEX = re.compile(r"\b(?:PL\d{26}|\d{26})\b")
CREDIT_CARD_REGEX = re.compile(r"\b(?:\d{4}[- ]?){3}\d{4}\b")
AGE_REGEX = re.compile(r"\b\d{1,3}\s*(?:lat|lata|roku życia|r\.ż\.)\b", re.IGNORECASE)
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


def is_valid_pesel(pesel: str) -> bool:
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


def is_valid_credit_card(number: str) -> bool:
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


def is_whitespace(token) -> bool:
    return any(ch in whitespace for ch in token.text)


def placeholder_for_token(token) -> str:
    mask_name = getattr(token._, "mask", None)
    if mask_name == "persname_mask":
        if getattr(token._, "priv_name", False):
            return "{name}"
        if getattr(token._, "priv_last_name", False):
            return "{surname}"
        return "{name}"
    if mask_name == "contact_mask":
        if "@" in token.text or "Q" in token.text or "©" in token.text:
            return "{email}"
        return "{phone}"
    if mask_name == "address_mask":
        return "{address}"
    if mask_name == "date_mask":
        return "{date}"
    if mask_name == "id_numbers_mask":
        if is_valid_pesel(token.text):
            return "{pesel}"
        return "{document-number}"
    if mask_name == "orgname_mask":
        lower_text = token.text.lower()
        if any(
            keyword in lower_text
            for keyword in ["szkoła", "liceum", "uniwersytet", "politechnika", "akademia"]
        ):
            return "{school-name}"
        return "{company}"
    if mask_name == "cash_mask":
        return "{cash}"
    return MASK_PLACEHOLDERS.get(mask_name, "{secret}")


def build_regex_spans(text: str):
    spans = []

    def add_span(start: int, end: int, placeholder: str):
        for existing_start, existing_end, _ in spans:
            if not (end <= existing_start or start >= existing_end):
                return
        spans.append((start, end, placeholder))

    for match in PESEL_REGEX.finditer(text):
        if is_valid_pesel(match.group(0)):
            add_span(match.start(), match.end(), "{pesel}")

    for match in PESEL_CONTEXT_REGEX.finditer(text):
        start = match.start(1)
        end = match.end(1)
        add_span(start, end, "{pesel}")

    for match in BANK_ACCOUNT_REGEX.finditer(text):
        add_span(match.start(), match.end(), "{bank-account}")

    for match in CREDIT_CARD_REGEX.finditer(text):
        if is_valid_credit_card(match.group(0)):
            add_span(match.start(), match.end(), "{credit-card-number}")

    pattern_placeholders = [
        (AGE_REGEX, "{age}"),
        (DOB_REGEX, "{date-of-birth}"),
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
        (PHONE_REGEX, "{phone}"),
    ]

    for pattern, placeholder in pattern_placeholders:
        for match in pattern.finditer(text):
            add_span(match.start(), match.end(), placeholder)

    spans.sort(key=lambda span: span[0])
    return spans


def compress_placeholders(text: str) -> str:
    text = re.sub(r"(?:\{address\})(?:\s+\{address\})+", "{address}", text)
    return text


def mask_with_labels(text, nlp, masked_components):
    doc = nlp(text)
    enabled_masks = [
        component for component, enabled in masked_components.items() if enabled
    ]
    regex_spans = build_regex_spans(text)
    span_index = 0
    current_span = regex_spans[span_index] if regex_spans else None
    output_parts = []
    for token in doc:
        while current_span and token.idx >= current_span[1]:
            span_index += 1
            current_span = (
                regex_spans[span_index] if span_index < len(regex_spans) else None
            )
        if current_span and current_span[0] <= token.idx < current_span[1]:
            if token.idx == current_span[0]:
                output_parts.append(current_span[2] + token.whitespace_)
            continue
        mask_name = getattr(token._, "mask", None)
        if (
            mask_name in enabled_masks
            and not token.is_punct
            and not is_whitespace(token)
        ):
            output_parts.append(placeholder_for_token(token) + token.whitespace_)
        elif (
            "id_numbers_mask" in enabled_masks
            and not token.is_punct
            and not is_whitespace(token)
            and is_valid_pesel(token.text)
        ):
            output_parts.append("{pesel}" + token.whitespace_)
        else:
            output_parts.append(token.text_with_ws)
    result = "".join(output_parts)
    result = compress_placeholders(result)
    return result


def print_comparison(original: str, masked: str, index: int) -> None:
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


nlp = spacy.load("pl_nask")
nlp = add_pipeline(nlp)

test_data_path = "nask_train/anonymized.txt"

with open(test_data_path, "r", encoding="utf-8") as f:
    test_lines = [line.strip() for line in f.readlines()[:25]]

for idx, text in enumerate(test_lines):
    masked_text = mask_with_labels(text, nlp, masked_components)
    print_comparison(text, masked_text, idx)
