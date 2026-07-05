import json
import re
from pathlib import Path

from core.config import ROOT_DIR


class NTGKnowledge:
    def __init__(self, base_path=None):
        self.base_path = Path(base_path or ROOT_DIR / "knowledge" / "NTG")

    def load_json(self, filename):
        path = self.base_path / filename
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def imported_summaries(self):
        summaries_dir = self.base_path / "summaries"
        if not summaries_dir.exists():
            return []

        summaries = []
        for path in sorted(summaries_dir.glob("*_summary.json")):
            with path.open("r", encoding="utf-8") as file:
                summaries.append(json.load(file))
        return summaries

    def summary(self):
        return {
            "definitions": self.load_json("definitions.json"),
            "notation": self.load_json("notation.json"),
            "hypotheses": self.load_json("hypotheses.json"),
            "imported_documents": self.imported_summaries(),
        }

    def search(self, query):
        documents = self.imported_summaries()
        tokens = re.findall(r"\w+", query.casefold())
        document_words = {"artigo", "documento", "pdf", "importado", "texto"}
        stop_words = {
            "que", "você", "voce", "acha", "qual", "quais", "como", "sobre",
            "para", "este", "esse", "esta", "essa", "meu", "minha", "dele",
        }
        references_document = any(word in tokens for word in document_words)
        terms = [
            token
            for token in tokens
            if len(token) > 2
            and token not in stop_words
            and token not in document_words
        ]

        if references_document and not terms and documents:
            return [self._latest_document_result(documents)]
        if not terms:
            return []

        results = []
        for document in documents:
            searchable = json.dumps(document, ensure_ascii=False).casefold()
            score = sum(searchable.count(term) for term in terms)
            if score:
                results.append(
                    {
                        "score": score,
                        "retrieval_reason": "palavras-chave",
                        "document": document,
                    }
                )
        if results:
            return sorted(results, key=lambda item: item["score"], reverse=True)

        if references_document and documents:
            return [self._latest_document_result(documents)]
        return []

    @staticmethod
    def _latest_document_result(documents):
        latest = max(
            documents,
            key=lambda document: document.get("imported_at", ""),
        )
        return {
            "score": 0,
            "retrieval_reason": "documento importado mais recente",
            "document": latest,
        }

    def as_text(self):
        return json.dumps(self.summary(), indent=2, ensure_ascii=False)
