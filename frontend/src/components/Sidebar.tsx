import {
  Atom,
  Bot,
  BrainCircuit,
  FlaskConical,
  GalleryHorizontal,
  MessageSquare,
  Network,
  Plus,
  Settings,
  Wrench
} from "lucide-react";

type Model = { id: string; name: string; available: boolean };
type Agent = { name: string; status: string };

const nav = [
  ["Chat", MessageSquare],
  ["Laboratorio", FlaskConical],
  ["Memoria", BrainCircuit],
  ["Grafo", Network],
  ["Artigos", GalleryHorizontal],
  ["Ferramentas", Wrench],
  ["Configuracoes", Settings]
] as const;

export function Sidebar({ models, agents }: { models: Model[]; agents: Agent[] }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">
          <Atom size={27} />
        </div>
        <div>
          <strong>DeepStructureAI</strong>
          <span>NTG Research Assistant</span>
        </div>
      </div>

      <section>
        <h2>Navegacao</h2>
        <nav className="nav-list">
          {nav.map(([label, Icon], index) => (
            <button className={index === 0 ? "active" : ""} key={label} title={label}>
              <Icon size={18} />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      </section>

      <section>
        <h2>Agentes</h2>
        <div className="compact-list">
          {agents.map((agent) => (
            <div key={agent.name} className="list-row">
              <Bot size={16} />
              <span>{agent.name}</span>
              <i className={agent.status === "online" ? "available" : "idle"} />
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2>Modelos</h2>
        <div className="compact-list">
          {models.map((model) => (
            <div key={model.id} className="list-row">
              <span className="model-initial">{model.name.slice(0, 2)}</span>
              <span>{model.name}</span>
              <i className={model.available ? "available" : "idle"} />
            </div>
          ))}
          <div className="list-row muted">
            <Plus size={16} />
            <span>Adicionar modelo</span>
          </div>
        </div>
      </section>

      <div className="profile">
        <div className="avatar">DS</div>
        <div>
          <strong>DeepStructureAI</strong>
          <span>Pesquisador</span>
        </div>
      </div>
    </aside>
  );
}
