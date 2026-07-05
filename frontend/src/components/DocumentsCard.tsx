import { FileText, Upload } from "lucide-react";
import { ChangeEvent, useRef, useState } from "react";

type Doc = { name: string; size: number };

function formatSize(size: number) {
  if (size > 1024 * 1024) return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  if (size > 1024) return `${Math.round(size / 1024)} KB`;
  return `${size} B`;
}

type Props = {
  documents: Doc[];
  onImport: (file: File) => Promise<void>;
};

export function DocumentsCard({ documents, onImport }: Props) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [status, setStatus] = useState("");

  async function handleFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;

    setStatus("Importando...");
    try {
      await onImport(file);
      setStatus("Documento importado");
    } catch {
      setStatus("Falha ao importar");
    }
  }

  return (
    <section className="panel-card lower-card">
      <div className="card-title-row">
        <h2>Documentos recentes</h2>
        <button className="icon-chip" onClick={() => inputRef.current?.click()} title="Importar documento">
          <Upload size={16} />
        </button>
      </div>
      <input
        accept=".pdf,.tex,.md,.json,.txt"
        className="hidden-input"
        onChange={handleFile}
        ref={inputRef}
        type="file"
      />
      <div className="metric-list tight">
        {documents.slice(0, 4).map((doc) => (
          <div className="metric-row" key={doc.name}>
            <FileText size={17} />
            <span>{doc.name}</span>
            <small>{formatSize(doc.size)}</small>
          </div>
        ))}
      </div>
      {status && <p className="card-status">{status}</p>}
      <button className="link-button">Ver todos</button>
    </section>
  );
}
