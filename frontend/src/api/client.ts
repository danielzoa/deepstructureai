const configuredApiUrl = import.meta.env.VITE_API_URL;
const isLocalHost =
  typeof window !== "undefined" &&
  ["localhost", "127.0.0.1"].includes(window.location.hostname);
const API_URL = configuredApiUrl || "http://localhost:8000";
const DEMO_MODE =
  import.meta.env.VITE_DEMO_MODE === "true" || (!configuredApiUrl && !isLocalHost);

export function getClientConfig() {
  return {
    apiUrl: API_URL,
    demoMode: DEMO_MODE,
    configuredApiUrl: configuredApiUrl || "",
    hostname: typeof window !== "undefined" ? window.location.hostname : ""
  };
}

export type ChatMessage = {
  role: "assistant" | "user";
  content: string;
  meta?: string;
  createdAt?: string;
};

export type DocumentPreview = {
  name: string;
  path: string;
  size: number;
  suffix: string;
  content: string;
  truncated: boolean;
  readable: boolean;
  warning?: string;
};

const mockGraph = {
  nodes: [
    { id: "ntg", label: "NTG" },
    { id: "navier", label: "Navier-Stokes 3D" },
    { id: "vorticidade", label: "Vorticidade" },
    { id: "pressao", label: "Pressão Anisotrópica" },
    { id: "nao-comutatividade", label: "Não Comutatividade" },
    { id: "materia-escura", label: "Matéria Escura" },
    { id: "rigidez", label: "Rigidez Espectral" },
    { id: "energia", label: "Energia" },
    { id: "transporte", label: "Transporte" }
  ],
  edges: []
};

async function request<T>(path: string, options?: RequestInit, fallback?: T): Promise<T> {
  if (DEMO_MODE && fallback !== undefined) return fallback;
  try {
    const response = await fetch(`${API_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return (await response.json()) as T;
  } catch {
    if (fallback !== undefined) return fallback;
    throw new Error("API unavailable");
  }
}

export const api = {
  getHealth: () =>
    request("/api/health", undefined, {
      status: "demo",
      glmConfigured: false,
      ollamaAvailable: false
    }),
  getReadiness: () =>
    request("/api/readiness", undefined, {
      status: DEMO_MODE ? "demo" : "offline",
      project: "DeepStructureAI",
      frontendOrigins: [],
      configuredModels: [],
      modelStatus: {},
      uploadDirectory: "knowledge/NTG/imports/web_uploads",
      uploadDirectoryExists: false,
      documentsCount: 0,
      warnings: DEMO_MODE ? ["frontend_demo_mode"] : ["api_unavailable"]
    }),
  getModels: () =>
    request("/api/models", undefined, [
      { id: "glm", name: "GLM / Z.AI", available: false },
      { id: "gemini", name: "Gemini", available: false },
      { id: "groq", name: "Groq", available: false },
      { id: "deepseek", name: "DeepSeek", available: false },
      { id: "ollama", name: "Ollama Local", available: false }
    ]),
  getAgents: () =>
    request("/api/agents", undefined, [
      { name: "Planner", status: "online" },
      { name: "Researcher", status: "online" },
      { name: "Critic", status: "standby" },
      { name: "Writer", status: "online" },
      { name: "Reviewer", status: "standby" }
    ]),
  getSummary: () =>
    request("/api/summary", undefined, {
      nodes: 121,
      relations: 152,
      clusters: 17,
      concepts: 89,
      semanticMemorySize: 12.4,
      scientificMemorySize: 8.7,
      laboratorySize: 6.1,
      documentsCount: 4
    }),
  getGraph: () => request("/api/graph", undefined, mockGraph),
  getMemory: () =>
    request("/api/memory", undefined, [
      { name: "Memória Semântica", size: 12.4 },
      { name: "Memória Científica", size: 8.7 },
      { name: "Knowledge Graph", size: 15.2 },
      { name: "Laboratório", size: 6.1 }
    ]),
  getLabStatus: () =>
    request("/api/lab/status", undefined, {
      project: "Controle de Enstrofia em NS 3D",
      hypothesis: "Ativa",
      evidenceCount: 3,
      testsCount: 2,
      progress: 68
    }),
  getDocuments: () =>
    request("/api/documents", undefined, [
      { name: "NTG.pdf", size: 245000 },
      { name: "calculos_ntg.tex", size: 18000 },
      { name: "hipóteses.md", size: 12000 },
      { name: "enstrofia_ntg.tex", size: 9000 }
    ]),
  readDocument: (path: string) =>
    request(
      `/api/documents/read?path=${encodeURIComponent(path)}`,
      undefined,
      {
        name: path.split("/").pop() || "documento",
        path,
        size: 0,
        suffix: "",
        content: "Leitura disponível quando o backend real estiver conectado.",
        truncated: false,
        readable: false,
        warning: "demo_mode"
      } as DocumentPreview
    ),
  importDocument: (name: string, contentBase64: string) =>
    request(
      "/api/documents/import",
      {
        method: "POST",
        body: JSON.stringify({ name, contentBase64 })
      },
      {
        name,
        path: `demo/${name}`,
        size: Math.round((contentBase64.length * 3) / 4),
        imported: false
      }
    ),
  getActivity: () =>
    request("/api/activity", undefined, [
      { time: "10:45", event: "Grafo atualizado" },
      { time: "10:44", event: "Evidência adicionada" },
      { time: "10:43", event: "Pesquisa concluída" },
      { time: "10:42", event: "PDF importado" }
    ]),
  getRouterStatus: () =>
    request("/api/router/status", undefined, {
      models: [],
      routes: {},
      activeRoutes: {}
    }),
  getChatHistory: () =>
    request("/api/chat/history", undefined, {
      messages: [] as ChatMessage[]
    }),
  clearChatHistory: () =>
    request(
      "/api/chat/history",
      {
        method: "DELETE"
      },
      { cleared: true }
    ),
  testRouter: (mode = "chat", dryRun = true) =>
    request(
      "/api/router/test",
      {
        method: "POST",
        body: JSON.stringify({ message: "Responda apenas: ok", mode, model: "auto", dryRun })
      },
      {
        mode,
        model: "mock",
        chain: ["mock"],
        dryRun
      }
    ),
  sendChatMessage: (message: string, mode = "chat", model = "glm") =>
    request(
      "/api/chat",
      {
        method: "POST",
        body: JSON.stringify({ message, mode, model })
      },
      {
        answer: `Modo demo ativo. Pergunta recebida: ${message}`,
        model: "demo",
        mode,
        sources: [],
        warnings: ["demo_mode"]
      }
    ),
  runCommand: (command: string) =>
    request(
      "/api/command",
      {
        method: "POST",
        body: JSON.stringify({ command })
      },
      { output: "Comando executado em modo demo.", blocked: false, warnings: ["demo_mode"] }
    )
};
