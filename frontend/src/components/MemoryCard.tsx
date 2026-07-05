import { BrainCircuit, Database, FlaskConical, Network } from "lucide-react";

type Item = { name: string; size: number };
const icons = [Database, BrainCircuit, Network, FlaskConical];

export function MemoryCard({ items, onOpen }: { items: Item[]; onOpen: () => void }) {
  return (
    <section className="panel-card">
      <h2>Memoria</h2>
      <div className="metric-list">
        {items.map((item, index) => {
          const Icon = icons[index % icons.length];
          return (
            <div className="metric-row" key={item.name}>
              <Icon size={17} />
              <span>{item.name}</span>
              <small>{item.size} MB</small>
            </div>
          );
        })}
      </div>
      <button className="link-button" onClick={onOpen}>Ver todas</button>
    </section>
  );
}
