import {
  Atom,
  BrainCircuit,
  FlaskConical,
  GalleryHorizontal,
  MessageSquare,
  Network,
  Settings
} from "lucide-react";

type Model = { id: string; name: string; available: boolean };
type Agent = { name: string; status: string };
export type ViewId = "chat" | "lab" | "memory" | "graph" | "articles" | "tools" | "settings" | "activity";

const nav = [
  ["chat", "Chat", MessageSquare],
  ["articles", "Documentos", GalleryHorizontal],
  ["graph", "Grafo", Network],
  ["lab", "Laboratorio", FlaskConical],
  ["memory", "Memoria", BrainCircuit],
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

export function Sidebar({ activeView, onNavigate }: Props) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">
          <Atom size={25} />
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

      <div className="profile">
        <div className="avatar">DS</div>
        <div>
          <strong>Research</strong>
          <span>Workspace</span>
        </div>
      </div>
    </aside>
  );
}
