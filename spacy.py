from typing import Literal
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
import logging
import os


class SpacyAnonymizer:
    def __init__(self, log, analyzers_lock, analyzers):
        self.log = self.default_logger if log is None else log
        self.analyzers_lock = analyzers_lock
        self.analyzers = analyzers

    def default_logger(self):
        log = logging.getLogger('default_logger - console only')
        if len(log.handlers) == 0:
            log.setLevel(logging.DEBUG)
            c_handler = logging.StreamHandler()
            c_handler.setLevel(logging.DEBUG)
            c_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
            log.addHandler(c_handler)
        return log

    def anonymize_text(self, sample_text: str, language: str = "en", min_len: int = 4):
        default_language = "en"
        spacy_models = {
            "en": "./spacy_models/en_core_web_md-3.8.0",
            "de": "./spacy_models/de_core_news_md-3.8.0",
            "fr": "./spacy_models/fr_core_news_md-3.8.0",
            "es": "./spacy_models/es_core_news_md-3.8.0",
            "it": "./spacy_models/it_core_news_md-3.8.0",
        }

        if len(sample_text) < min_len:
            return sample_text

        supported_language = language if language in spacy_models else default_language
        with self.analyzers_lock:
            if self.analyzers.get(supported_language, None) is None:
                model_path = spacy_models[supported_language]
                if not os.path.exists(model_path):
                    raise ValueError(f"Model for language `{language}` not found in `{model_path}`")
                self.log.debug(f'Loading analyzer for language `{language}`')
                nlp_conf = {"nlp_engine_name": "spacy", "models": [{"lang_code": language, "model_name": model_path}]}
                provider = NlpEngineProvider(nlp_configuration=nlp_conf)
                nlp_engine = provider.create_engine()
                analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=[supported_language])
                self.analyzers[supported_language] = analyzer
            else:
                analyzer = self.analyzers[supported_language]

        # region -= analyze and mark/anonymize text =-
        results = analyzer.analyze(
            text=sample_text,
            language=supported_language,
            entities=[
                "PERSON",
                "EMAIL_ADDRESS",
                "PHONE_NUMBER",
            ],
        )
        transformations = []
        for result in results:
            original_text = sample_text[result.start:result.end]
            if action == "mark":
                transformed_text = f"<{marking_tag}>{original_text}</{marking_tag}>"
            elif action == "replace":
                transformed_text = replace_with
            else:
                raise ValueError(f"Unknown action `{action}`")
            transformations.append({
                "start": result.start,
                "end": result.end,
                "entity_type": result.entity_type,
                "text": transformed_text
            })
        anonymized_text = sample_text
        for transform in sorted(transformations, key=lambda x: x["start"], reverse=True):
            anonymized_text = (
                    anonymized_text[:transform["start"]] +
                    transform["text"] +
                    anonymized_text[transform["end"]:]
            )
        # endregion

        return anonymized_text


if __name__ == "__main__":
    pass
