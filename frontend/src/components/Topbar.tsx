import { Menu, Settings, Sun } from "lucide-react";

import { StatusBadge } from "./StatusBadge";

type Props = {
  connected: boolean;
  onMenu: () => void;
  onSettings: () => void;
  onThemeToggle: () => void;
};

export function Topbar({ connected, onMenu, onSettings, onThemeToggle }: Props) {
  return (
    <header className="topbar">
      <button className="icon-button" onClick={onMenu} title="Menu">
        <Menu size={20} />
      </button>
      <div className="topbar-actions">
        <StatusBadge online={connected} label={connected ? "GLM conectado" : "Modo local/demo"} />
        <button className="icon-button" onClick={onThemeToggle} title="Tema">
          <Sun size={19} />
        </button>
        <button className="icon-button" onClick={onSettings} title="Configuracoes">
          <Settings size={19} />
        </button>
      </div>
    </header>
  );
}
