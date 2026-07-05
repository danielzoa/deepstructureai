import { SendHorizontal } from "lucide-react";
import { FormEvent, useState } from "react";

import type { ChatMessage } from "../api/client";

const quick = ["/about", "/health", "/team", "/models", "/benchmark"];
const commands = ["/import_ntg", "/graph build", "/lab start", "/semantic search", "/validate idea"];
const modes = [
  ["auto", "Auto"],
  ["chat", "Chat"],
  ["fast", "Rapido"],
  ["document", "Documento"],
  ["critic", "Critico"],
  ["code", "Codigo"],
  ["lab", "Laboratorio"],
  ["offline", "Offline"]
];

type Props = {
  messages: ChatMessage[];
  mode: string;
  onModeChange: (mode: string) => void;
  onSend: (message: string) => void;
};

export function ChatPanel({ messages, mode, onModeChange, onSend }: Props) {
  const [value, setValue] = useState("");

  function submit(event: FormEvent) {
    event.preventDefault();
    const text = value.trim();
    if (!text) return;
    setValue("");
    onSend(text);
  }

  return (
    <section className="chat-shell">
      <div className="section-heading">
        <h1>Chat</h1>
        <p>Converse com os agentes de pesquisa</p>
      </div>

      <div className="mode-tabs" role="tablist" aria-label="Modo do chat">
        {modes.map(([value, label]) => (
          <button
            className={mode === value ? "selected" : ""}
            key={value}
            onClick={() => onModeChange(value)}
            type="button"
          >
            {label}
          </button>
        ))}
      </div>

      <div className="chat-card">
        <div className="assistant-head">
          <div className="mini-logo">DS</div>
          <div>
            <strong>DeepStructureAI</strong>
            <span>Assistente de Pesquisa Cientifica</span>
          </div>
        </div>

        <div className="message-stream">
          {messages.map((message, index) => (
            <article className={`message ${message.role}`} key={`${message.role}-${index}`}>
              <p>{message.content}</p>
              {message.meta && <small>{message.meta}</small>}
            </article>
          ))}
        </div>

        <div className="quick-actions">
          {quick.map((item) => (
            <button key={item} onClick={() => onSend(item)}>
              {item}
            </button>
          ))}
        </div>
      </div>

      <form className="chat-input" onSubmit={submit}>
        <input
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder="Digite sua pergunta ou comando..."
        />
        <button title="Enviar" type="submit">
          <SendHorizontal size={20} />
        </button>
      </form>

      <div className="command-strip">
        <span>Comandos rapidos:</span>
        {commands.map((command) => (
          <button key={command} onClick={() => onSend(command)}>
            {command}
          </button>
        ))}
      </div>
    </section>
  );
}
