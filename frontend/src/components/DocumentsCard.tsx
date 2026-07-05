import { FileText } from "lucide-react";

type Doc = { name: string; size: number };

function formatSize(size: number) {
  if (size > 1024 * 1024) return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  if (size > 1024) return `${Math.round(size / 1024)} KB`;
  return `${size} B`;
}

export function DocumentsCard({ documents }: { documents: Doc[] }) {
  return (
    <section className="panel-card lower-card">
      <h2>Documentos recentes</h2>
      <div className="metric-list tight">
        {documents.slice(0, 4).map((doc) => (
          <div className="metric-row" key={doc.name}>
            <FileText size={17} />
            <span>{doc.name}</span>
            <small>{formatSize(doc.size)}</small>
          </div>
        ))}
      </div>
      <button className="link-button">Ver todos</button>
    </section>
  );
}
