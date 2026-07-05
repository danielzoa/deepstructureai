# DeepStructureAI MVP Web

DeepStructureAI agora tem um MVP web com backend FastAPI, frontend React/Vite e suporte configurável ao GLM/Z.AI.

## Instalar

```bash
python -m pip install -r backend/requirements.txt
cd frontend
npm install
```

## Configurar `.env`

Copie `.env.example` para `.env` na raiz e preencha:

```env
ZAI_API_KEY=sua_chave
ZAI_BASE_URL=https://api.z.ai/api/paas/v4
ZAI_MODEL=GLM-5.2
DEFAULT_MODEL=glm
DEFAULT_FAST_MODEL=groq
DEFAULT_DOCUMENT_MODEL=gemini
DEFAULT_CRITIC_MODEL=deepseek
DEFAULT_OFFLINE_MODEL=ollama

GEMINI_API_KEY=sua_chave
GROQ_API_KEY=sua_chave
DEEPSEEK_API_KEY=sua_chave
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

Sem alguma chave, o backend não quebra: ele pula aquele modelo e segue a cadeia de fallback.

## Sinergia Multi-IA

Rotas do chat:

- `chat`: GLM > Gemini > Groq > Ollama > mock
- `fast`: Groq > GLM > Ollama > mock
- `document`: Gemini > GLM > Ollama > mock
- `critic`: DeepSeek > GLM > Gemini > Ollama > mock
- `code`: DeepSeek > GLM > Groq > Ollama > mock
- `lab`: DeepSeek > GLM > Gemini > Ollama > mock
- `offline`: Ollama > mock

Endpoints:

- `GET /api/models`
- `GET /api/router/status`
- `POST /api/chat`
- `POST /api/router/test`
- `POST /api/documents/import`

## Importar Documentos

No frontend, use o botão de upload no card "Documentos recentes".

O backend aceita `.pdf`, `.tex`, `.md`, `.json` e `.txt`, com limite de 10 MB, e grava em:

```text
knowledge/NTG/imports/web_uploads/
```

## Rodar Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Rodar Frontend

```bash
cd frontend
npm run dev
```

Abra `http://127.0.0.1:5173`.

## Testar GLM

1. Configure `ZAI_API_KEY` no `.env`.
2. Rode o backend.
3. Envie uma mensagem no chat ou use:

```bash
curl -X POST http://127.0.0.1:8000/api/chat -H "Content-Type: application/json" -d "{\"message\":\"Explique NTG em 3 pontos\",\"mode\":\"chat\",\"model\":\"glm\"}"
```

## GitHub

```bash
git add .
git commit -m "MVP web DeepStructureAI with GLM support"
gh repo create deepstructureai --private --source=. --remote=origin --push
```

Se o `gh` não estiver autenticado:

```bash
git remote add origin URL_DO_REPOSITORIO
git branch -M main
git push -u origin main
```

## Cloudflare Pages

Publique apenas o frontend:

- Root directory: `frontend`
- Framework: Vite
- Build command: `npm run build`
- Output directory: `dist`
- Env var enquanto o backend for local: `VITE_DEMO_MODE=true`
- Quando o backend estiver hospedado: `VITE_API_URL=https://sua-api.com`

Via Wrangler:

```bash
cd frontend
npm run build
npx wrangler pages deploy dist --project-name deepstructureai
```

## Backend em Produção

O backend pode ser publicado como container Docker. Este repositório já inclui:

- `Dockerfile` para rodar o FastAPI.
- `.dockerignore` para não enviar cache, `.env`, `node_modules` ou build local.
- `render.yaml` como ponto de partida para Render.

No provedor do backend, configure as chaves como variáveis secretas:

```env
ZAI_API_KEY=
GEMINI_API_KEY=
GROQ_API_KEY=
DEEPSEEK_API_KEY=
FRONTEND_ORIGINS=https://deepstructureai.pages.dev
```

Depois que a API estiver online, configure no Cloudflare Pages:

```env
VITE_API_URL=https://sua-api-do-deepstructureai
VITE_DEMO_MODE=false
```

Faça um novo build/deploy do frontend para o site usar o backend real.

## Mock/Demo

- Chat retorna resposta demo quando nenhuma IA da rota está disponível ou todas falham.
- Grafo usa `data/knowledge_graph.json` ou `output/graph/knowledge_graph.json`; se falhar, usa grafo NTG mockado.
- Atividade usa `logs/agent.log`; se não houver log legível, usa eventos mockados.
- Laboratório e memórias usam arquivos reais para tamanho/status e completam lacunas com valores seguros.

## Próximos Passos

- Hospedar o backend FastAPI em um serviço Python.
- Conectar comandos do `/command` ao dispatcher CLI com lista permitida.
- Criar tela completa do grafo.
- Adicionar upload/importação de PDF pelo frontend.
- Salvar histórico de chat por sessão.
