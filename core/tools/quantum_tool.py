from core.tools.base_tool import BaseTool


class QuantumTool(BaseTool):
    name = "Quantum"

    def run(self, query):
        query = query.lower().strip()

        if "bell" in query:
            return self.bell()

        return "QuantumTool ativo. Use: /quantum bell"

    def bell(self):
        from qiskit import QuantumCircuit, transpile
        from qiskit_aer import AerSimulator

        qc = QuantumCircuit(2, 2)

        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])

        simulator = AerSimulator()
        compiled = transpile(qc, simulator)
        result = simulator.run(compiled, shots=1024).result()
        counts = result.get_counts()

        return f"""
Circuito de Bell criado.

Operações:
1. H no qubit 0
2. CNOT entre qubit 0 e qubit 1
3. Medição dos dois qubits

Resultado esperado:
Estados 00 e 11 aparecem com probabilidades próximas de 50% cada.

Contagens:
{counts}
"""