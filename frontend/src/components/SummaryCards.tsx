type Summary = {
  nodes: number;
  relations: number;
  clusters: number;
  concepts: number;
};

export function SummaryCards({ summary }: { summary: Summary }) {
  return (
    <section className="panel-card summary-card">
      <h2>Resumo</h2>
      <div className="summary-grid">
        <div>
          <strong>{summary.nodes}</strong>
          <span>Nós</span>
        </div>
        <div>
          <strong>{summary.relations}</strong>
          <span>Relações</span>
        </div>
        <div>
          <strong>{summary.clusters}</strong>
          <span>Clusters</span>
        </div>
        <div>
          <strong>{summary.concepts}</strong>
          <span>Conceitos</span>
        </div>
      </div>
    </section>
  );
}
