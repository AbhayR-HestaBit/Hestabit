# Deployment Architecture & Notes 

## Deployment Architecture Diagram
```text
[User Browser]
      |
(Streamlit UI: localhost:8501)
      |
      V
[FastAPI Server] <= [Local Memory JSON]
      |
      |=> /ask 
      |   |--> ContextBuilder
      |   |--> OpenRouter API 
      |   \--> Evaluator 
      |
      |=> /ask-image
      |   |--> Text/Image Embedding Match
      |   \--> OpenRouter API
      |
      \=> /ask-sql
              |--> SQL Generator and Validator
              |--> Local SQLite
              \--> OpenRouter API 
```

## API Endpoints

### 1. Text RAG (`/ask`)
```bash
curl -X POST http://localhost:8000/ask \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the core features of this RAG system?", "session_id": "test-user-1"}'
```

### 2. SQL QA (`/ask-sql`)
*Note: Uses the real customer dataset.*
```bash
curl -X POST http://localhost:8000/ask-sql \
     -H "Content-Type: application/json" \
     -d '{"question": "How many customers in Denmark?", "session_id": "test-user-1"}'
```

### 3. Image Search (`/ask-image`)
**Text to Image:**
```bash
curl -X POST http://localhost:8000/ask-image \
     -H "Content-Type: application/json" \
     -d '{"query": "images with diagrams", "mode": "text2image"}'
```

**Image to Answer (using placeholder base64):**
```bash
curl -X POST http://localhost:8000/ask-image \
     -H "Content-Type: application/json" \
     -d '{"query": "What is in this image?", "mode": "img2ans", "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="}'
```

### 4. Sessions (`/sessions`)
```bash
curl -X GET http://localhost:8000/sessions
```

## Execution Strategy
To avoid Out-Of-Memory (OOM) errors and slow-downs:
- **API Optimization:** With the newly attached OpenRouter API, memory problems are eliminated. Do not worry about running out of RAM as the Local LLM is fully disabled.
- Do not use multiple workers for Uvicorn (keep it single-process) as FAISS indices should only be loaded once per port.

## Commands

```bash
# Terminal 1 - API
source week7_env/bin/activate
uvicorn src.deployment.app:app --host 0.0.0.0 --port 8000

# Terminal 2 - Streamlit
source week7_env/bin/activate
streamlit run src.deployment.streamlit_app.py
```

## Minimal Code Snippet
**FastAPI Request Logging & Tracing**
```python
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    # automatically generate a request ID and log the path
    request_id = str(uuid.uuid4())
    logger.info("Request %s %s %s", request_id, request.method, request.url.path)
    response = await call_next(request)
    return response
```

## Screenshots
![FastAPI logs](screenshots/BE.png)

![FastAPI logs](screenshots/BE.png)
