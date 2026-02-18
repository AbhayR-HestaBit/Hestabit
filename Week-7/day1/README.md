# Day 1: Local RAG Implementation Summary

##  Folder Structure
```text
week7_rag/
 RAG-ARCHITECTURE.md
 src/
     config/
        model.yaml
     data/
        chunks/
        cleaned/
        embeddings/
        raw/
     embeddings/
        embedder.py
     evaluation/
     generator/
        llm_client.py
     logs/
     models/
        mistral-7b-instruct-v0.2.Q5_0.gguf
     pipelines/
        ingest.py
        run_pipeline.py
     prompts/
        rag_prompt.txt
     retriever/
        query_engine.py
     utils/
        text_utils.py
     vectorstore/
         vector_manager.py
```

## Tasks Done

- Ingestion Pipeline with PDF/DOCX/CSV/TXT files.
- Integrated `BGE-small-en-v1.5` CPU-based embeddings.
- Built `VectorStoreManager` using FAISS.
- Retrieval and RAG logic with plain text output.
- Created `run_pipeline.py` CLI.

## Code Snippet
**Embedder Class:**
```python
class Embedder:
    # converts raw text chunks into numerical vectors
    def __init__(self, model_name='BAAI/bge-small-en-v1.5', device='cpu'):
        self.model = SentenceTransformer(model_name, device=device)
        self.batch_size = 32
```

## Commands 

```bash
# To ingest and index text data into FAISS:
source week7_env/bin/activate
python3 -m src.pipelines.run_pipeline --all
```
![Ingest](screenshots/pipeline.png)

```bash
# To query
python3 -m src.pipelines.run_pipeline --query "Where does David Figueroa lives?" --no_llm
```
![Query](screenshots/query.png)

