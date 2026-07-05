import json


class KnowledgeManager:
    def __init__(
        self,
        obsidian=None,
        scientific_memory=None,
        ntg_knowledge=None,
        knowledge_graph=None,
    ):
        self.obsidian = obsidian
        self.scientific_memory = scientific_memory
        self.ntg_knowledge = ntg_knowledge
        self.knowledge_graph = knowledge_graph

    def retrieve(self, query):
        parts = []

        if self.obsidian:
            parts.append("=== OBSIDIAN ===")
            parts.append(str(self.obsidian.search(query)))

        if self.scientific_memory:
            parts.append("=== SCIENTIFIC MEMORY ===")
            parts.append(self.scientific_memory.summary())

        if self.ntg_knowledge:
            parts.append("=== NTG KNOWLEDGE ===")
            parts.append(self.ntg_knowledge.as_text())

        if self.knowledge_graph:
            parts.append("=== KNOWLEDGE GRAPH ===")
            parts.append(
                json.dumps(
                    self.knowledge_graph.search(query),
                    indent=2,
                    ensure_ascii=False,
                )
            )

        return "\n\n".join(parts)
