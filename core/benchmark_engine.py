import time


class BenchmarkEngine:
    def __init__(self, llm):
        self.llm = llm

    def run_simple(self):
        tests = [
            {
                "name": "explicação",
                "prompt": "Explique em poucas linhas o que é Navier-Stokes."
            },
            {
                "name": "código",
                "prompt": "Escreva uma função Python que calcule fatorial."
            },
            {
                "name": "crítica",
                "prompt": "Critique a hipótese: P0 controla o stretching da vorticidade."
            }
        ]

        results = []

        for model_name in self.llm.registry.names():
            for test in tests:
                start = time.time()

                try:
                    response = self.llm.ask_model(
                        model_name=model_name,
                        system_prompt="Você está sendo avaliado em um benchmark curto.",
                        user_prompt=test["prompt"],
                        fallback=None
                    )

                    elapsed = round(time.time() - start, 2)

                    results.append({
                        "model": model_name,
                        "test": test["name"],
                        "success": True,
                        "time": elapsed,
                        "preview": response[:300]
                    })

                except Exception as e:
                    results.append({
                        "model": model_name,
                        "test": test["name"],
                        "success": False,
                        "time": None,
                        "error": str(e)
                    })

        return results

    def report(self):
        results = self.run_simple()

        lines = ["Benchmark Results\n"]

        for r in results:
            lines.append(f"Modelo: {r['model']}")
            lines.append(f"Teste: {r['test']}")
            lines.append(f"Sucesso: {r['success']}")
            lines.append(f"Tempo: {r['time']}")
            lines.append(f"Preview: {r.get('preview', r.get('error', ''))}")
            lines.append("-" * 40)

        return "\n".join(lines)