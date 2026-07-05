import { Network } from "lucide-react";

type Node = { id: string; label: string };

const positions = [
  [50, 50],
  [25, 18],
  [50, 15],
  [76, 26],
  [80, 56],
  [74, 78],
  [50, 84],
  [30, 74],
  [25, 50]
];

export function KnowledgeGraphCard({ nodes, onOpen }: { nodes: Node[]; onOpen: () => void }) {
  const visible = nodes.length ? nodes.slice(0, 9) : [];
  return (
    <section className="panel-card graph-card">
      <h2>Grafo de Conhecimento</h2>
      <div className="graph-viz">
        <svg viewBox="0 0 100 100" aria-hidden="true">
          {visible.slice(1).map((node, index) => (
            <line
              key={node.id}
              x1="50"
              y1="50"
              x2={positions[index + 1][0]}
              y2={positions[index + 1][1]}
            />
          ))}
        </svg>
        {visible.map((node, index) => (
          <div
            className={index === 0 ? "graph-node center" : "graph-node"}
            key={node.id}
            style={{ left: `${positions[index][0]}%`, top: `${positions[index][1]}%` }}
          >
            {index === 0 ? "NTG" : node.label}
          </div>
        ))}
      </div>
      <button className="wide-button" onClick={onOpen}>
        <Network size={16} />
        Abrir grafo completo
      </button>
    </section>
  );
}
