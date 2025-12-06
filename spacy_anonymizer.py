from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
import logging
import os
import threading
import spacy


class SpacyAnonymizer:
    def __init__(self, log=None, analyzers_lock=None, analyzers=None):
        self.log = self.default_logger() if log is None else log
        self.analyzers_lock = analyzers_lock if analyzers_lock is not None else threading.Lock()
        self.analyzers = analyzers if analyzers is not None else {}

    def default_logger(self):
        log = logging.getLogger('default_logger - console only')
        if len(log.handlers) == 0:
            log.setLevel(logging.DEBUG)
            c_handler = logging.StreamHandler()
            c_handler.setLevel(logging.DEBUG)
            c_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
            log.addHandler(c_handler)
        return log

    def anonymize_text(self, sample_text: str, min_len: int = 4):
        if len(sample_text) < min_len:
            return sample_text

        with self.analyzers_lock:
            if self.analyzers.get("pl", None) is None:
                model_path = "pl_nask"

                try:
                    spacy.load(model_path)
                except OSError:
                    raise ValueError(
                        f"Model `{model_path}` not installed. Install it with: pip install {model_path}")

                self.log.debug(f'Loading analyzer for Polish language')
                nlp_conf = {
                    "nlp_engine_name": "spacy",
                    "models": [{"lang_code": "pl", "model_name": model_path}]
                }
                provider = NlpEngineProvider(nlp_configuration=nlp_conf)
                nlp_engine = provider.create_engine()
                analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["pl"])
                self.analyzers["pl"] = analyzer
            else:
                analyzer = self.analyzers["pl"]

        # Analyze and mark/anonymize text
        results = analyzer.analyze(
            text=sample_text,
            language="pl",
            entities=[
                "PERSON",
                "EMAIL_ADDRESS",
                "PHONE_NUMBER",
                "CREDIT_CARD",
                "CRYPTO",
                "DATE_TIME",
                "IBAN_CODE",
                "IP_ADDRESS",
                "LOCATION",
                "MEDICAL_LICENSE",
                "NRP",
                "Organization",
                "URL",
                "US_BANK_NUMBER",
                "US_DRIVER_LICENSE",
                "US_ITIN",
                "US_PASSPORT",
                "US_SSN",
            ],
        )

        transformations = []
        for result in results:
            transformations.append({
                "start": result.start,
                "end": result.end,
                "entity_type": result.entity_type,
                "text": '[PII]'
            })

        anonymized_text = sample_text
        for transform in sorted(transformations, key=lambda x: x["start"], reverse=True):
            anonymized_text = (
                    anonymized_text[:transform["start"]] +
                    transform["text"] +
                    anonymized_text[transform["end"]:]
            )

        return anonymized_text


if __name__ == "__main__":
    test_data_path = 'nask_train/_anonymized.txt'

    anonymizer = SpacyAnonymizer()

    if not os.path.exists(test_data_path):
        print(f"Błąd: Plik {test_data_path} nie istnieje!")
        print("\nUżywam przykładowych danych testowych:")
        test_lines = [
            "JEDNOSTKA PROJEKTUJĄCA Gabinety Wiese al. Orzechowa 37/41 27-233 Siemianowice Śląskie tel +48 513 078 320 fax 514 588 331",
        ]
    else:
        # Wczytanie 10 linijek z pliku
        with open(test_data_path, 'r', encoding='utf-8') as f:
            test_lines = [line.strip() for line in f.readlines()[:10]]

    print("=" * 80)
    print("ANONIMIZACJA TEKSTU - PORÓWNANIE")
    print("=" * 80)

    for i, line in enumerate(test_lines, 1):
        if not line:  # Pomijamy puste linie
            continue

        print(f"\n--- Przykład {i} ---")
        print(f"ORYGINAŁ:     {line}")

        # Anonimizacja
        anonymized = anonymizer.anonymize_text(line)
        print(f"ZANONIMIZOWANY: {anonymized}")

    print("\n" + "=" * 80)
