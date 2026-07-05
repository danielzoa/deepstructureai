class DemoManager:
    def __init__(self, agent):
        self.agent = agent

    def about(self):
        return """
DeepStructureAI

Tipo:
Plataforma multiagente para pesquisa científica assistida por IA.

Componentes:
✓ Research Team
✓ Consensus Engine
✓ Research Sessions
✓ Knowledge Graph
✓ Scientific Memory
✓ Knowledge Manager
✓ Model Router
✓ Model Registry
✓ Obsidian
✓ QuantumTool
✓ Ollama / Hermes

Objetivo:
Apoiar pesquisa científica, organização de hipóteses, análise crítica, memória estruturada e colaboração entre modelos.
"""

    def health(self):
        checks = []

        items = [
            ("LLM", "llm"),
            ("Research Team", "team"),
            ("Consensus Engine", "consensus"),
            ("Research Sessions", "research_sessions"),
            ("Knowledge Graph", "knowledge_graph"),
            ("Scientific Memory", "scientific_memory"),
            ("Knowledge Manager", "knowledge_manager"),
            ("Obsidian", "obsidian"),
            ("Tool Manager", "tool_manager"),
        ]

        for label, attr in items:
            checks.append(f"{'✓' if hasattr(self.agent, attr) else '✗'} {label}")

        return "DeepStructureAI Health\n\n" + "\n".join(checks)

    def demo(self):
        return """
DeepStructureAI Demo

Rode estes comandos:

1. /health
2. /team
3. /models
4. /graph
5. /smemory
6. /session start Demo | DeepStructureAI | Teste rápido do sistema
7. /consensus_short Explique o que é a hipótese H1
8. /quantum bell
9. /session events
10. /session finish

Fluxo demonstrado:
diagnóstico → modelos → equipe → consenso → ferramenta científica → sessão persistente.
"""