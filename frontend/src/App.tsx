import { useEffect, useState } from "react";
import type { ReactNode } from "react";

import { api, type ChatMessage } from "./api/client";
import { ActivityCard } from "./components/ActivityCard";
import { ChatPanel } from "./components/ChatPanel";
import { DocumentsCard } from "./components/DocumentsCard";
import { KnowledgeGraphCard } from "./components/KnowledgeGraphCard";
import { LabCard } from "./components/LabCard";
import { MemoryCard } from "./components/MemoryCard";
import { Sidebar, type ViewId } from "./components/Sidebar";
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

const toolCommands = ["/about", "/health", "/team", "/models", "/benchmark", "/graph stats", "/graph build", "/lab start", "/semantic search", "/validate idea", "/documents", "/activity"];
const chatStorageKey = "deepstructureai.chat.v1";

export default function App() {
  const [activeView, setActiveView] = useState<ViewId>("chat");
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
  const [routerStatus, setRouterStatus] = useState<any>({ routes: {}, activeRoutes: {}, models: [] });
  const [messages, setMessages] = useState<ChatMessage[]>([initialMessage]);
  const [chatMode, setChatMode] = useState("auto");
  const [toolOutput, setToolOutput] = useState("Selecione uma ferramenta para executar.");
  const [darkMode, setDarkMode] = useState(false);
  const [detailSearch, setDetailSearch] = useState("");

  useEffect(() => {
    refreshAll();
    const stored = window.localStorage.getItem(chatStorageKey);
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as ChatMessage[];
        if (Array.isArray(parsed) && parsed.length) {
          setMessages(parsed);
        }
      } catch {
        window.localStorage.removeItem(chatStorageKey);
      }
    }
  }, []);

  useEffect(() => {
    window.localStorage.setItem(chatStorageKey, JSON.stringify(messages.slice(-80)));
  }, [messages]);

  async function refreshAll() {
    const [
      healthData,
      modelsData,
      agentsData,
      summaryData,
      graphData,
      memoryData,
      labData,
      docsData,
      activityData,
      routerData
    ] = await Promise.all([
      api.getHealth(),
      api.getModels(),
      api.getAgents(),
      api.getSummary(),
      api.getGraph(),
      api.getMemory(),
      api.getLabStatus(),
      api.getDocuments(),
      api.getActivity(),
      api.getRouterStatus()
    ]);
    setHealth(healthData as any);
    setModels(modelsData as any[]);
    setAgents(agentsData as any[]);
    setSummary(summaryData as Summary);
    setGraph(graphData as any);
    setMemory(memoryData as any[]);
    setLab(labData);
    setDocuments(docsData as any[]);
    setActivity(activityData as any[]);
    setRouterStatus(routerData);
  }

  async function send(message: string) {
    setMessages((current) => [...current, { role: "user", content: message }]);

    if (message.trim().startsWith("/")) {
      const response = await api.runCommand(message);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: response.output,
          meta: response.warnings?.length ? `Comando | aviso: ${response.warnings.join(", ")}` : "Comando"
        }
      ]);
      return;
    }

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

  async function importDocument(file: File) {
    const dataUrl = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result));
      reader.onerror = () => reject(reader.error);
      reader.readAsDataURL(file);
    });
    const contentBase64 = dataUrl.split(",")[1] || "";
    await api.importDocument(file.name, contentBase64);
    const [docsData, summaryData, activityData] = await Promise.all([
      api.getDocuments(),
      api.getSummary(),
      api.getActivity()
    ]);
    setDocuments(docsData as any[]);
    setSummary(summaryData as Summary);
    setActivity(activityData as any[]);
  }

  async function runTool(command: string) {
    setActiveView("tools");
    const response = await api.runCommand(command);
    setToolOutput(response.output);
  }

  function clearChat() {
    setMessages([initialMessage]);
    window.localStorage.removeItem(chatStorageKey);
  }

  function exportChat() {
    const markdown = messages
      .map((message) => `## ${message.role === "user" ? "Usuario" : "DeepStructureAI"}\n\n${message.content}\n\n${message.meta ? `_${message.meta}_\n` : ""}`)
      .join("\n");
    const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `deepstructureai-chat-${new Date().toISOString().slice(0, 10)}.md`;
    link.click();
    URL.revokeObjectURL(url);
  }

  function filterRows(items: Array<[string, string]>) {
    const term = detailSearch.trim().toLowerCase();
    if (!term) return items;
    return items.filter(([label, value]) => `${label} ${value}`.toLowerCase().includes(term));
  }

  function openView(view: ViewId) {
    setDetailSearch("");
    setActiveView(view);
  }

  function selectAgent(agent: any) {
    setActiveView("chat");
    setChatMode(agent.name === "Critic" || agent.name === "Reviewer" ? "critic" : agent.name === "Writer" ? "document" : "auto");
    setMessages((current) => [
      ...current,
      {
        role: "assistant",
        content: `${agent.name} selecionado. Envie uma pergunta para trabalhar com esse perfil.`,
        meta: "Agente"
      }
    ]);
  }

  function selectModel(model: any) {
    setActiveView("settings");
    setToolOutput(`${model.name}: ${model.available ? "disponivel" : "indisponivel ou sem chave configurada"}`);
  }

  function renderMainView() {
    if (activeView === "chat") {
      return (
        <div className="dashboard-grid">
          <div className="main-column">
            <ChatPanel
              messages={messages}
              mode={chatMode}
              onClear={clearChat}
              onExport={exportChat}
              onModeChange={setChatMode}
              onSend={send}
            />
            <div className="bottom-grid">
              <LabCard lab={lab} onOpen={() => openView("lab")} />
              <DocumentsCard documents={documents} onImport={importDocument} onOpen={() => openView("articles")} />
            </div>
          </div>
          <aside className="right-column">
            <SummaryCards summary={summary} />
            <KnowledgeGraphCard nodes={graph.nodes} onOpen={() => openView("graph")} />
            <MemoryCard items={memory} onOpen={() => openView("memory")} />
            <ActivityCard activity={activity} onOpen={() => openView("activity")} />
          </aside>
        </div>
      );
    }

    return (
      <div className="detail-layout">
        {activeView === "lab" && (
          <DetailPanel title="Laboratorio" description="Status do laboratorio ativo e comandos de pesquisa.">
            <MetricGrid items={[
              ["Projeto", lab.project],
              ["Hipotese", lab.hypothesis],
              ["Evidencias", `${lab.evidenceCount}`],
              ["Testes", `${lab.testsCount}`],
              ["Progresso", `${lab.progress}%`]
            ]} />
            <button className="wide-button" onClick={() => runTool("/lab start")}>Atualizar laboratorio</button>
          </DetailPanel>
        )}

        {activeView === "memory" && (
          <DetailPanel title="Memoria" description="Resumo das memorias usadas pelo DeepStructureAI.">
            <SearchBox value={detailSearch} onChange={setDetailSearch} placeholder="Filtrar memorias..." />
            <DataList items={filterRows(memory.map((item) => [item.name, `${item.size} MB`]))} />
            <button className="wide-button" onClick={() => runTool("/semantic search")}>Testar busca semantica</button>
          </DetailPanel>
        )}

        {activeView === "graph" && (
          <DetailPanel title="Grafo de Conhecimento" description="Nos e relacoes carregados do knowledge graph.">
            <MetricGrid items={[["Nos", `${graph.nodes.length}`], ["Relacoes", `${graph.edges.length}`], ["Clusters", `${summary.clusters}`], ["Conceitos", `${summary.concepts}`]]} />
            <SearchBox value={detailSearch} onChange={setDetailSearch} placeholder="Filtrar nos do grafo..." />
            <DataList items={filterRows(graph.nodes.map((node) => [node.label || node.id, node.id])).slice(0, 80)} />
            <button className="wide-button" onClick={() => runTool("/graph build")}>Recalcular resumo do grafo</button>
          </DetailPanel>
        )}

        {activeView === "articles" && (
          <DetailPanel title="Artigos e Documentos" description="Documentos encontrados em NTG, imports, output e data.">
            <DocumentsCard documents={documents} onImport={importDocument} onOpen={() => openView("articles")} />
            <SearchBox value={detailSearch} onChange={setDetailSearch} placeholder="Filtrar documentos..." />
            <DataList items={filterRows(documents.map((doc) => [doc.name, doc.path || `${doc.size} bytes`]))} />
          </DetailPanel>
        )}

        {activeView === "tools" && (
          <DetailPanel title="Ferramentas" description="Comandos seguros conectados ao backend do MVP.">
            <div className="tool-grid">
              {toolCommands.map((command) => (
                <button key={command} onClick={() => runTool(command)}>{command}</button>
              ))}
            </div>
            <pre className="output-box">{toolOutput}</pre>
          </DetailPanel>
        )}

        {activeView === "settings" && (
          <DetailPanel title="Configuracoes" description="Estado de modelos, rotas e ambiente local.">
            <MetricGrid items={[
              ["API", (health as any).status || "demo"],
              ["GLM", (health as any).glmConfigured ? "configurado" : "sem chave"],
              ["Ollama", (health as any).ollamaAvailable ? "online" : "offline"],
              ["Tema", darkMode ? "escuro" : "claro"]
            ]} />
            <h3>Modelos</h3>
            <DataList items={models.map((model) => [model.name, model.available ? "disponivel" : "indisponivel"])} />
            <h3>Rotas ativas</h3>
            <pre className="output-box">{JSON.stringify(routerStatus.activeRoutes || {}, null, 2)}</pre>
          </DetailPanel>
        )}

        {activeView === "activity" && (
          <DetailPanel title="Atividade Recente" description="Eventos recentes do agente e fallback de atividade do MVP.">
            <SearchBox value={detailSearch} onChange={setDetailSearch} placeholder="Filtrar atividade..." />
            <DataList items={filterRows(activity.map((item) => [item.time || "--:--", item.event]))} />
            <button className="wide-button" onClick={() => runTool("/activity")}>Ver JSON da atividade</button>
          </DetailPanel>
        )}
      </div>
    );
  }

  return (
    <div className={`app-shell ${darkMode ? "theme-dark" : ""}`}>
      <Sidebar
        activeView={activeView}
        agents={agents}
        models={models}
        onNavigate={openView}
        onSelectAgent={selectAgent}
        onSelectModel={selectModel}
      />
      <main className="workspace">
        <Topbar
          connected={Boolean((health as any).glmConfigured)}
          onMenu={() => openView("chat")}
          onRefresh={refreshAll}
          onSettings={() => openView("settings")}
          onThemeToggle={() => setDarkMode((current) => !current)}
        />
        {renderMainView()}
      </main>
    </div>
  );
}

function DetailPanel({ title, description, children }: { title: string; description: string; children: ReactNode }) {
  return (
    <section className="detail-panel">
      <div className="section-heading">
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      <div className="panel-card detail-card">{children}</div>
    </section>
  );
}

function MetricGrid({ items }: { items: Array<[string, string]> }) {
  return (
    <div className="detail-metrics">
      {items.map(([label, value]) => (
        <div key={label}>
          <span>{label}</span>
          <strong>{value}</strong>
        </div>
      ))}
    </div>
  );
}

function DataList({ items }: { items: Array<[string, string]> }) {
  return (
    <div className="data-list">
      {items.map(([label, value], index) => (
        <div key={`${label}-${index}`}>
          <strong>{label}</strong>
          <span>{value}</span>
        </div>
      ))}
    </div>
  );
}

function SearchBox({ value, onChange, placeholder }: { value: string; onChange: (value: string) => void; placeholder: string }) {
  return (
    <div className="search-row">
      <input value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} />
    </div>
  );
}
