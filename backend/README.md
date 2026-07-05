# DeepStructureAI Backend

FastAPI MVP for the DeepStructureAI web interface.

## Run

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API reads project data from the repository root and uses mock NTG data when a data source is unavailable.

## Production

The repository root includes a `Dockerfile` and `render.yaml`.

Required public configuration:

```env
FRONTEND_ORIGINS=https://deepstructureai.pages.dev
```

Optional model secrets:

```env
ZAI_API_KEY=
GEMINI_API_KEY=
GROQ_API_KEY=
DEEPSEEK_API_KEY=
```

Missing model keys do not break the API; the router falls back to the next available model or mock mode.
