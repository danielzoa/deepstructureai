import { useEffect, useState } from "react";

import { api, type ChatMessage } from "./api/client";
import { ActivityCard } from "./components/ActivityCard";
import { ChatPanel } from "./components/ChatPanel";
import { DocumentsCard } from "./components/DocumentsCard";
import { KnowledgeGraphCard } from "./components/KnowledgeGraphCard";
import { LabCard } from "./components/LabCard";
import { MemoryCard } from "./components/MemoryCard";
import { Sidebar } from "./components/Sidebar";
import { SummaryCards } from "./components/SummaryCards";
import { Topbar } from "./components/Topbar";

type Summary = {
  nodes: number;
  relations: number;
  clusters: number;
  concepts: number;
  semanticMemorySize: number;
  scientificMemorySize: number;
  laboratorySize: number;
  documentsCount: number;
};

const initialMessage: ChatMessage = {
  role: "assistant",
  content:
    "Ola! Sou seu assistente de pesquisa cientifica. Como posso ajudar sua investigacao hoje?\n\nVoce pode importar PDFs, analisar conceitos, construir grafos de conhecimento, validar hipoteses e gerar relatorios.",
  meta: "DeepStructureAI"
};

export default function App() {
  const [health, setHealth] = useState({ glmConfigured: false });
  const [models, setModels] = useState<any[]>([]);
  const [agents, setAgents] = useState<any[]>([]);
  const [summary, setSummary] = useState<Summary>({
    nodes: 121,
    relations: 152,
    clusters: 17,
    concepts: 89,
    semanticMemorySize: 12.4,
    scientificMemorySize: 8.7,
    laboratorySize: 6.1,
    documentsCount: 4
  });
  const [graph, setGraph] = useState<{ nodes: any[]; edges: any[] }>({ nodes: [], edges: [] });
  const [memory, setMemory] = useState<any[]>([]);
  const [lab, setLab] = useState<any>({
    project: "Controle de Enstrofia em NS 3D",
    hypothesis: "Ativa",
    evidenceCount: 3,
    testsCount: 2,
    progress: 68
  });
  const [documents, setDocuments] = useState<any[]>([]);
  const [activity, setActivity] = useState<any[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([initialMessage]);
  const [chatMode, setChatMode] = useState("auto");

  useEffect(() => {
    Promise.all([
      api.getHealth(),
      api.getModels(),
      api.getAgents(),
      api.getSummary(),
      api.getGraph(),
      api.getMemory(),
      api.getLabStatus(),
      api.getDocuments(),
      api.getActivity()
    ]).then(([healthData, modelsData, agentsData, summaryData, graphData, memoryData, labData, docsData, activityData]) => {
      setHealth(healthData as any);
      setModels(modelsData as any[]);
      setAgents(agentsData as any[]);
      setSummary(summaryData as Summary);
      setGraph(graphData as any);
      setMemory(memoryData as any[]);
      setLab(labData);
      setDocuments(docsData as any[]);
      setActivity(activityData as any[]);
    });
  }, []);

  async function send(message: string) {
    setMessages((current) => [...current, { role: "user", content: message }]);
    const response = await api.sendChatMessage(message, chatMode, "auto");
    setMessages((current) => [
      ...current,
      {
        role: "assistant",
        content: response.answer,
        meta: `Modelo: ${response.model}${response.warnings?.length ? " | aviso: demo/fallback" : ""}`
      }
    ]);
  }

  return (
    <div className="app-shell">
      <Sidebar models={models} agents={agents} />
      <main className="workspace">
        <Topbar connected={Boolean((health as any).glmConfigured)} />
        <div className="dashboard-grid">
          <div className="main-column">
            <ChatPanel
              messages={messages}
              mode={chatMode}
              onModeChange={setChatMode}
              onSend={send}
            />
            <div className="bottom-grid">
              <LabCard lab={lab} />
              <DocumentsCard documents={documents} />
            </div>
          </div>
          <aside className="right-column">
            <SummaryCards summary={summary} />
            <KnowledgeGraphCard nodes={graph.nodes} />
            <MemoryCard items={memory} />
            <ActivityCard activity={activity} />
          </aside>
        </div>
      </main>
    </div>
  );
}
