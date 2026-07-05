# DeepStructureAI MVP Web

DeepStructureAI agora tem um MVP web com backend FastAPI, frontend React/Vite e suporte configuravel ao GLM/Z.AI.

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

Sem alguma chave, o backend nao quebra: ele pula aquele modelo e segue a cadeia de fallback.

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

Se o `gh` nao estiver autenticado:

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

## Mock/Demo

- Chat retorna resposta demo quando nenhuma IA da rota esta disponivel ou todas falham.
- Grafo usa `data/knowledge_graph.json` ou `output/graph/knowledge_graph.json`; se falhar, usa grafo NTG mockado.
- Atividade usa `logs/agent.log`; se nao houver log legivel, usa eventos mockados.
- Laboratorio e memorias usam arquivos reais para tamanho/status e completam lacunas com valores seguros.

## Proximos Passos

- Hospedar o backend FastAPI em um servico Python.
- Conectar comandos do `/command` ao dispatcher CLI com lista permitida.
- Criar tela completa do grafo.
- Adicionar upload/importacao de PDF pelo frontend.
- Salvar historico de chat por sessao.
