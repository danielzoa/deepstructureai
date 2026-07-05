from core.llm import LLM


class KnowledgeCurator:

    def __init__(self, llm=None):
        self.llm = llm or LLM()

    def analyze(self, text):

        system = """
Você é um curador científico.

Sua tarefa é classificar informações produzidas durante uma pesquisa.

Escolha apenas uma categoria:

- hypothesis
- experiment
- decision
- paper
- question
- note

Retorne também:

- confidence (0-100)
- save (true/false)
- justification

Responda apenas em JSON.
"""

        return self.llm.ask(system, text)