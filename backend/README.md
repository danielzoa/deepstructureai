# DeepStructureAI Backend

FastAPI MVP for the DeepStructureAI web interface.

## Run

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API reads project data from the repository root and uses mock NTG data when a data source is unavailable.
