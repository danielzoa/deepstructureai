from dataclasses import dataclass, field


@dataclass
class ResearchContext:
    question: str = ""
    project: str = ""
    goal: str = ""

    obsidian_context: str = ""
    obsidian_notes: list = field(default_factory=list)

    notes: list = field(default_factory=list)
    tasks: list = field(default_factory=list)
    hypotheses: list = field(default_factory=list)
    history: list = field(default_factory=list)

    plan: str = ""
    criticisms: list = field(default_factory=list)
    experiments: list = field(default_factory=list)
    references: list = field(default_factory=list)
    next_steps: list = field(default_factory=list)

    web_results: list = field(default_factory=list)
    tool_results: list = field(default_factory=list)
    profile_context: str = ""
    knowledge_context: str = ""
    semantic_context: str = ""
    lab_context: str = ""
    lab_mode: bool = False
    graph_context: str = ""
    obsidian_context: str = ""
    obsidian_notes: list = field(default_factory=list)

    answer: str = ""

    def reset_outputs(self):
        self.plan = ""
        self.criticisms.clear()
        self.hypotheses.clear()
        self.history.clear()
        self.web_results.clear()
        self.tool_results.clear()
        self.answer = ""
