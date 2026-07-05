# DeepStructureAI Production Runbook

Este roteiro transforma o MVP/demo em ambiente online real.

## 1. Hospedar Backend

Opções já preparadas no repositório:

- Render: use `render.yaml`.
- Railway: use `railway.json`.
- Docker/VPS: use `Dockerfile`.
- Procfile-based hosts: use `Procfile`.

Health check:

```text
/api/health
```

## 2. Configurar Secrets

Configure somente no provedor do backend. Não coloque no frontend.

```env
ZAI_API_KEY=
GEMINI_API_KEY=
GROQ_API_KEY=
DEEPSEEK_API_KEY=
FRONTEND_ORIGINS=https://deepstructureai.pages.dev
```

Chaves ausentes não quebram a API; o router usa fallback.

## 3. Conectar Cloudflare Pages

Depois que a API estiver online, configure o build do Pages:

```env
VITE_API_URL=https://sua-api-online
VITE_DEMO_MODE=false
```

Depois faça novo deploy do frontend.

## 4. Testar Ponta a Ponta

Rode localmente:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-production.ps1 -ApiUrl https://sua-api-online -SiteUrl https://deepstructureai.pages.dev -RunTests -RunBuild
```

O script verifica:

- Git limpo.
- Testes do backend.
- Build do frontend.
- `/api/health`.
- `/api/readiness`.
- `/api/router/status`.
- `/api/chat`.
- Site publicado.

## 5. Polir Produção

Checklist final:

- Ativar CI copiando `docs/github-actions-ci.yml` para `.github/workflows/ci.yml` com token que tenha permissão `workflow`.
- Definir domínio final.
- Proteger o site/API se o projeto for privado.
- Planejar backup de `data/web_state.db` ou trocar para Postgres.
- Ativar logs do provedor.
- Rodar o script de produção depois de cada deploy relevante.
