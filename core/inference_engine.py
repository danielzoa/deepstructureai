class InferenceEngine:
    def __init__(
        self,
        task_analyzer=None,
        model_router=None,
        tool_dispatcher=None,
    ):
        self.task_analyzer = task_analyzer
        self.model_router = model_router
        self.tool_dispatcher = tool_dispatcher

    def plan(self, message):
        task = "chat"

        if self.task_analyzer:
            task = self.task_analyzer.analyze(message)

        model_route = None

        if self.model_router:
            model_route = self.model_router.decide(task)

        tools = []

        if self.tool_dispatcher:
            tool = self.tool_dispatcher.decide(message)
            if tool:
                tools.append(tool)

        workflow = self.choose_workflow(task)

        knowledge = self.choose_knowledge(task)

        return {
            "task": task,
            "workflow": workflow,
            "model_route": model_route,
            "tools": tools,
            "knowledge": knowledge,
        }

    def choose_workflow(self, task):
        if task in ["research", "math"]:
            return "research"

        if task == "coding":
            return "coding"

        if task == "pdf":
            return "document"

        return "chat"

    def choose_knowledge(self, task):
        if task in ["research", "math"]:
            return [
                "ScientificMemory",
                "Obsidian",
                "NTGKnowledge",
            ]

        if task == "pdf":
            return [
                "PDFs",
                "Obsidian",
            ]

        return [
            "Memory",
        ]