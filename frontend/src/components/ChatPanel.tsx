import { Download, RotateCcw, SendHorizontal, Trash2 } from "lucide-react";
import { FormEvent, useState } from "react";

import type { ChatMessage } from "../api/client";

const modes = [
  ["auto", "Auto"],
  ["chat", "Chat"],
  ["fast", "Rapido"],
  ["document", "Documento"],
  ["critic", "Critico"],
  ["code", "Codigo"],
  ["lab", "Lab"]
];

type Props = {
  messages: ChatMessage[];
  mode: string;
  onClear: () => void;
  onExport: () => void;
  onModeChange: (mode: string) => void;
  onSend: (message: string) => void;
};

export function ChatPanel({ messages, mode, onClear, onExport, onModeChange, onSend }: Props) {
  const [value, setValue] = useState("");

  function submit(event: FormEvent) {
    event.preventDefault();
    const text = value.trim();
    if (!text) return;
    setValue("");
    onSend(text);
  }

  return (
    <section className="chat-shell calm-chat">
      <div className="chat-panel-head">
        <div>
          <h1>Chat</h1>
          <p>Pesquisa, escrita e analise com roteamento multi-IA.</p>
        </div>
        <div className="chat-tools">
          <button onClick={onExport} title="Exportar conversa" type="button">
            <Download size={16} />
          </button>
          <button onClick={() => onSend("/health")} title="Atualizar status" type="button">
            <RotateCcw size={16} />
          </button>
          <button onClick={onClear} title="Limpar conversa" type="button">
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      <div className="mode-tabs compact-tabs" role="tablist" aria-label="Modo do chat">
        {modes.map(([itemValue, label]) => (
          <button
            className={mode === itemValue ? "selected" : ""}
            key={itemValue}
            onClick={() => onModeChange(itemValue)}
            type="button"
          >
            {label}
          </button>
        ))}
      </div>

      <div className="chat-card">
        <div className="message-stream">
          {messages.map((message, index) => (
            <article className={`message ${message.role}`} key={`${message.role}-${index}`}>
              <p>{message.content}</p>
              {message.meta && <small>{message.meta}</small>}
            </article>
          ))}
        </div>
      </div>

      <form className="chat-input" onSubmit={submit}>
        <input
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder="Pergunte sobre sua pesquisa ou use /help..."
        />
        <button title="Enviar" type="submit">
          <SendHorizontal size={20} />
        </button>
      </form>
    </section>
  );
}
