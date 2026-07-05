import { useEffect, useState } from "react";
import type { ReactNode } from "react";

import { api, getClientConfig, type ChatMessage } from "./api/client";
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
    "Olá! Sou seu assistente de pesquisa científica. Como posso ajudar sua investigação hoje?\n\nVocê pode importar PDFs, analisar conceitos, construir grafos de conhecimento, validar hipóteses e gerar relatórios.",
  meta: "DeepStructureAI"
};

const toolCommands = ["/about", "/health", "/team", "/models", "/benchmark", "/graph stats", "/graph build", "/lab start", "/semantic search", "/validate idea", "/documents", "/activity"];
const chatStorageKey = "deepstructureai.chat.v1";
const routeModes = ["chat", "fast", "document", "critic", "code", "lab", "offline"];
const clientConfig = getClientConfig();

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
  const [readiness, setReadiness] = useState<any>({ status: "unknown", warnings: [] });
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
    } else {
      api.getChatHistory().then((history) => {
        if (history.messages?.length) {
          setMessages(history.messages);
        }
      });
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
      routerData,
      readinessData
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
      api.getRouterStatus(),
      api.getReadiness()
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
    setReadiness(readinessData);
  }

  async function send(message: string) {
    const trimmed = message.trim();
    if (!trimmed) return;
    setMessages((current) => [...current, { role: "user", content: trimmed }]);

    if (trimmed.startsWith("/")) {
      const response = await api.runCommand(trimmed);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: response.output,
          meta: response.warnings?.length ? `Comando | aviso: ${response.warnings.join(", ")}` : "Comando"
        }
      ]);
      refreshAll();
      return;
    }

    const response = await api.sendChatMessage(trimmed, chatMode, "auto");
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
    refreshAll();
  }

  async function testRoute(mode: string) {
    setActiveView("settings");
    const response = await api.testRouter(mode, true);
    setToolOutput(JSON.stringify(response, null, 2));
  }

  function exportJson(name: string, data: unknown) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `deepstructureai-${name}-${new Date().toISOString().slice(0, 10)}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  async function clearChat() {
    setMessages([initialMessage]);
    window.localStorage.removeItem(chatStorageKey);
    await api.clearChatHistory();
    refreshAll();
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
    setToolOutput(`${model.name}: ${model.available ? "disponível" : "indisponível ou sem chave configurada"}`);
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
          <DetailPanel title="Laboratório" description="Status do laboratório ativo e comandos de pesquisa.">
            <MetricGrid items={[
              ["Projeto", lab.project],
              ["Hipótese", lab.hypothesis],
              ["Evidências", `${lab.evidenceCount}`],
              ["Testes", `${lab.testsCount}`],
              ["Progresso", `${lab.progress}%`]
            ]} />
            <div className="action-row">
              <button className="wide-button" onClick={() => runTool("/lab start")}>Atualizar laboratório</button>
              <button className="wide-button" onClick={() => exportJson("laboratorio", lab)}>Exportar laboratório</button>
            </div>
          </DetailPanel>
        )}

        {activeView === "memory" && (
          <DetailPanel title="Memória" description="Resumo das memórias usadas pelo DeepStructureAI.">
            <SearchBox value={detailSearch} onChange={setDetailSearch} placeholder="Filtrar memórias..." />
            <DataList items={filterRows(memory.map((item) => [item.name, `${item.size} MB`]))} />
            <div className="action-row">
              <button className="wide-button" onClick={() => runTool("/semantic search")}>Testar busca semântica</button>
              <button className="wide-button" onClick={() => exportJson("memoria", memory)}>Exportar memória</button>
            </div>
          </DetailPanel>
        )}

        {activeView === "graph" && (
          <DetailPanel title="Grafo de Conhecimento" description="Nós e relações carregados do knowledge graph.">
            <MetricGrid items={[["Nós", `${graph.nodes.length}`], ["Relações", `${graph.edges.length}`], ["Clusters", `${summary.clusters}`], ["Conceitos", `${summary.concepts}`]]} />
            <SearchBox value={detailSearch} onChange={setDetailSearch} placeholder="Filtrar nós do grafo..." />
            <DataList items={filterRows(graph.nodes.map((node) => [node.label || node.id, node.id])).slice(0, 80)} />
            <div className="action-row">
              <button className="wide-button" onClick={() => runTool("/graph build")}>Recalcular resumo do grafo</button>
              <button className="wide-button" onClick={() => exportJson("grafo", graph)}>Exportar grafo</button>
            </div>
          </DetailPanel>
        )}

        {activeView === "articles" && (
          <DetailPanel title="Artigos e Documentos" description="Documentos encontrados em NTG, imports, output e data.">
            <DocumentsCard documents={documents} onImport={importDocument} onOpen={() => openView("articles")} />
            <SearchBox value={detailSearch} onChange={setDetailSearch} placeholder="Filtrar documentos..." />
            <DataList items={filterRows(documents.map((doc) => [doc.name, doc.path || `${doc.size} bytes`]))} />
            <button className="wide-button" onClick={() => exportJson("documentos", documents)}>Exportar documentos</button>
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
          <DetailPanel title="Configurações" description="Estado de modelos, rotas e ambiente local.">
            <MetricGrid items={[
              ["API", (health as any).status || "demo"],
              ["GLM", (health as any).glmConfigured ? "configurado" : "sem chave"],
              ["Ollama", (health as any).ollamaAvailable ? "online" : "offline"],
              ["Tema", darkMode ? "escuro" : "claro"]
            ]} />
            <h3>Prontidão</h3>
            <DataList items={[
              ["Frontend", clientConfig.demoMode ? "modo demo" : "conectado à API"],
              ["API URL", clientConfig.apiUrl],
              ["Backend", readiness.status || "desconhecido"],
              ["Modelos ativos", readiness.configuredModels?.length ? readiness.configuredModels.join(", ") : "nenhum"],
              ["Uploads", readiness.uploadDirectoryExists ? "diretório pronto" : "diretório não encontrado"],
              ["Avisos", readiness.warnings?.length ? readiness.warnings.join(", ") : "sem avisos"]
            ]} />
            <h3>Modelos</h3>
            <DataList items={models.map((model) => [model.name, model.available ? "disponível" : "indisponível"])} />
            <h3>Rotas ativas</h3>
            <div className="tool-grid">
              {routeModes.map((mode) => (
                <button key={mode} onClick={() => testRoute(mode)}>Testar {mode}</button>
              ))}
            </div>
            <pre className="output-box">{JSON.stringify(routerStatus.activeRoutes || {}, null, 2)}</pre>
            <pre className="output-box">{toolOutput}</pre>
          </DetailPanel>
        )}

        {activeView === "activity" && (
          <DetailPanel title="Atividade Recente" description="Eventos recentes do agente e fallback de atividade do MVP.">
            <SearchBox value={detailSearch} onChange={setDetailSearch} placeholder="Filtrar atividade..." />
            <DataList items={filterRows(activity.map((item) => [item.time || "--:--", item.event]))} />
            <div className="action-row">
              <button className="wide-button" onClick={() => runTool("/activity")}>Ver JSON da atividade</button>
              <button className="wide-button" onClick={() => exportJson("atividade", activity)}>Exportar atividade</button>
            </div>
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
