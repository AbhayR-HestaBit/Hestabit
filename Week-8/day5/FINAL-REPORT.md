# Final Report: Local LLM Deployment

## Files Involved
- `deploy/app.py`: FastAPI server for inference.
- `deploy/model_loader.py`: Efficient singleton for model management.
- `streamlit_app.py`: Interactive user interface.
- `DOCKERFILE`: Containerization instructions.

## Commands Run
To launch the production API:
```bash
uvicorn deploy.app:app --host 0.0.0.0 --port 8000
```
To run the evaluation UI:
```bash
streamlit run streamlit_app.py
```

## Implementation Highlights (FastAPI)
```python
@app.post("/generate")
def generate(req: GenerateRequest):
    llm = get_model()
    output = llm(req.prompt, max_tokens=req.max_tokens, temperature=req.temperature)
    return {"text": output["choices"][0]["text"].strip()}
```
