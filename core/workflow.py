import time


class Workflow:
    def __init__(self):
        self.steps = []

    def add(self, name, agent):
        self.steps.append((name, agent))

    def run(self, context, registry, bus):
        previous_agent = "Coordinator"

        for agent_name, agent in self.steps:
            bus.send(
                sender=previous_agent,
                receiver=agent_name,
                task="process",
                content=context.question,
            )

            start = time.perf_counter()

            agent.process(context)

            elapsed = time.perf_counter() - start

            registry.record_execution(
                agent_name,
                context,
                elapsed,
            )

            previous_agent = agent_name

        return context.answer