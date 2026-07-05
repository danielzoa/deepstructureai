import { FlaskConical, Microscope, TestTubeDiagonal } from "lucide-react";

type Lab = {
  project: string;
  hypothesis: string;
  evidenceCount: number;
  testsCount: number;
  progress: number;
};

export function LabCard({ lab }: { lab: Lab }) {
  return (
    <section className="panel-card lower-card">
      <h2>Laboratorio ativo</h2>
      <p className="subtle">Projeto Atual: {lab.project}</p>
      <div className="metric-list tight">
        <div className="metric-row">
          <FlaskConical size={17} />
          <span>Hipotese</span>
          <small className="green">{lab.hypothesis}</small>
        </div>
        <div className="metric-row">
          <Microscope size={17} />
          <span>Evidencias</span>
          <small>{lab.evidenceCount} coletadas</small>
        </div>
        <div className="metric-row">
          <TestTubeDiagonal size={17} />
          <span>Testes</span>
          <small>{lab.testsCount} realizados</small>
        </div>
        <div className="progress-line">
          <span>Progresso</span>
          <div>
            <i style={{ width: `${lab.progress}%` }} />
          </div>
          <strong>{lab.progress}%</strong>
        </div>
      </div>
    </section>
  );
}
