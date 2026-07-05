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
export type ViewId = "chat" | "lab" | "memory" | "graph" | "articles" | "tools" | "settings" | "activity";

const nav = [
  ["chat", "Chat", MessageSquare],
  ["lab", "Laboratorio", FlaskConical],
  ["memory", "Memoria", BrainCircuit],
  ["graph", "Grafo", Network],
  ["articles", "Artigos", GalleryHorizontal],
  ["tools", "Ferramentas", Wrench],
  ["settings", "Configuracoes", Settings]
] as const;

type Props = {
  models: Model[];
  agents: Agent[];
  activeView: ViewId;
  onNavigate: (view: ViewId) => void;
  onSelectAgent: (agent: Agent) => void;
  onSelectModel: (model: Model) => void;
};

export function Sidebar({ models, agents, activeView, onNavigate, onSelectAgent, onSelectModel }: Props) {
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
          {nav.map(([id, label, Icon]) => (
            <button
              className={activeView === id ? "active" : ""}
              key={id}
              onClick={() => onNavigate(id)}
              title={label}
            >
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
            <button key={agent.name} className="list-row" onClick={() => onSelectAgent(agent)}>
              <Bot size={16} />
              <span>{agent.name}</span>
              <i className={agent.status === "online" ? "available" : "idle"} />
            </button>
          ))}
        </div>
      </section>

      <section>
        <h2>Modelos</h2>
        <div className="compact-list">
          {models.map((model) => (
            <button key={model.id} className="list-row" onClick={() => onSelectModel(model)}>
              <span className="model-initial">{model.name.slice(0, 2)}</span>
              <span>{model.name}</span>
              <i className={model.available ? "available" : "idle"} />
            </button>
          ))}
          <button className="list-row muted" onClick={() => onNavigate("settings")}>
            <Plus size={16} />
            <span>Adicionar modelo</span>
          </button>
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
