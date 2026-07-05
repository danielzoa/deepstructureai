import { Menu, Settings, Sun } from "lucide-react";

import { StatusBadge } from "./StatusBadge";

export function Topbar({ connected }: { connected: boolean }) {
  return (
    <header className="topbar">
      <button className="icon-button" title="Menu">
        <Menu size={20} />
      </button>
      <div className="topbar-actions">
        <StatusBadge online={connected} label={connected ? "GLM conectado" : "Modo local/demo"} />
        <button className="icon-button" title="Tema">
          <Sun size={19} />
        </button>
        <button className="icon-button" title="Configuracoes">
          <Settings size={19} />
        </button>
      </div>
    </header>
  );
}
